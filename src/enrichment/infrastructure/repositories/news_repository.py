from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from sqlalchemy import and_, case, column, func, literal, select
from sqlalchemy import values as sa_values
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db.db import ReadSessionManager
from enrichment.domain.entities.new_chunk import NewsChunk
from enrichment.domain.repositories.news_repository_port import NewsRepositoryPort
from enrichment.domain.specs.news_serch_spec import NewsSearchContext
from enrichment.infrastructure.orm.news_chunk import NewsChunk as NewsChunkORM


class NewsRepository(NewsRepositoryPort):
    """뉴스 청크 리포지터리"""

    def __init__(self, session_manager: ReadSessionManager):
        self.session_manager = session_manager

    async def search(
        self,
        context: NewsSearchContext,
    ) -> Dict[UUID, List[NewsChunk]]:
        """
        여러 검색 쿼리를 한 방에 처리 (VALUES + LATERAL)
        회사당 limit_per_company 개 제한, similarity_threshold 이상만 반환
        """
        if not context.queries:
            return dict()

        # 1) 파라미터 테이블(가상 테이블) 생성: VALUES (company_id, start_date, end_date, qvec)
        #    -> 문자열 포맷팅 없이 안전하게 벡터 바인딩 (리스트 그대로)
        rows = [query.to_tuple() for query in context.queries]

        # SQLAlchemy VALUES 테이블 정의 (pgvector는 컬럼 타입 지정 불필요: 바인딩 시 드라이버가 처리)
        v = (
            sa_values(
                column("company_id", PG_UUID(as_uuid=True)),
                column("qvec"),
                column("start_date"),
                column("end_date"),
            )
            .data(rows)
            .alias("q")
        )

        # 2) 날짜 조건: end_date 가 None이면 upper bound 미적용
        date_pred = and_(
            NewsChunkORM.company_id == v.c.company_id,
            NewsChunkORM.created_at >= v.c.start_date,
            # end_date가 있으면 <= 비교, 없으면 True
            case(
                (v.c.end_date.isnot(None), NewsChunkORM.created_at <= v.c.end_date),
                else_=literal(True),
            ),
        )

        # 3) 거리/유사도: 코사인 기준 (1 - cosine_distance)
        dist = NewsChunkORM.vector.cosine_distance(v.c.qvec)
        sim = (literal(1.0) - dist).label("similarity_score")

        # 4) LATERAL 식으로 생각되는 조인 계획: 값 한 줄(q)마다 해당 범위의 뉴스에서 점수 계산
        ranked = (
            select(
                NewsChunkORM.id,
                NewsChunkORM.company_id,
                NewsChunkORM.title,
                NewsChunkORM.contents,
                sim,
                func.row_number()
                .over(
                    partition_by=NewsChunkORM.company_id,  # 회사별 상위 N
                    order_by=dist.asc(),  # 거리 오름차순 == 유사도 내림차순
                )
                .label("rn"),
            )
            .select_from(v.join(NewsChunkORM, date_pred))
            .where(sim >= context.similarity_threshold)
            .subquery("ranked")
        )

        # 5) 회사별 상위 limit_per_company만 남기고, 전체는 유사도 내림차순 정렬
        final_stmt = (
            select(
                ranked.c.id,
                ranked.c.company_id,
                ranked.c.title,
                ranked.c.contents,
                ranked.c.similarity_score,
            )
            .where(ranked.c.rn <= context.limit_per_company)
            .order_by(ranked.c.similarity_score.desc())
        )

        async with self.session_manager as session:
            result = await session.execute(final_stmt)
            rows = result.fetchall()

        # 6) 회사별 그룹핑
        chunks: Dict[UUID, List[NewsChunk]] = {}
        for r in rows:
            chunks.setdefault(r.company_id, []).append(
                NewsChunk(
                    id=r.id,
                    company_id=r.company_id,
                    title=r.title,
                    contents=r.contents,
                    similarity=r.similarity_score,
                )
            )
        return chunks
