from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from pgvector.sqlalchemy import Vector as PG_Vector
from sqlalchemy import and_, case, cast, column, func, literal, select
from sqlalchemy import values as sa_values
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db.db import ReadSessionManager
from enrichment.domain.entities.new_chunk import NewsChunk
from enrichment.domain.repositories.news_repository_port import NewsRepositoryPort
from enrichment.domain.specs.news_serch_spec import NewsSearchContext
from enrichment.infrastructure.orm.news_chunk import NewsChunk as NewsChunkORM


class NewsRepository(NewsRepositoryPort):
    """뉴스 청크 리포지터리

    벡터 유사도 검색을 통해 회사별 뉴스 청크를 조회하는 리포지터리입니다.
    """

    def __init__(self, session_manager: ReadSessionManager):
        self.session_manager = session_manager

    async def search(
        self,
        context: NewsSearchContext,
    ) -> Dict[UUID, List[NewsChunk]]:
        """
        여러 검색 쿼리를 한 번에 처리하여 회사별 뉴스 청크를 검색합니다.

        Args:
            context: 검색 컨텍스트 (쿼리 목록, 유사도 임계값, 회사당 제한 개수 포함)

        Returns:
            Dict[UUID, List[NewsChunk]]: 회사 ID를 키로 하고, 해당 회사의 뉴스 청크 목록을 값으로 하는 딕셔너리
        """
        if not context.queries:
            return dict()

        rows = [query.to_tuple() for query in context.queries]

        # VALUES 절을 사용하여 여러 검색 쿼리를 하나의 테이블로 생성
        # 이를 통해 배치 검색이 가능하며, 여러 회사의 뉴스를 한 번의 쿼리로 검색할 수 있습니다.
        v = (
            sa_values(
                column("company_id", PG_UUID(as_uuid=True)),  # 회사 UUID
                column(
                    "qvec", PG_Vector(1536)
                ),  # 1536차원 임베딩 벡터 (OpenAI text-embedding-3-small 모델)
                column("start_date"),  # 검색 시작 날짜
                column("end_date"),  # 검색 종료 날짜 (optional)
            )
            .data(rows)
            .alias("q")
        )

        # 날짜 필터링 조건 생성
        # 1. 회사 ID가 일치해야 함
        # 2. 뉴스 생성일이 재직 시작 날짜 이후여야 함
        # 3. 퇴사 날짜가 있는 경우, 뉴스 생성일이 퇴사 날짜 이전이어야 함
        date_pred = and_(
            NewsChunkORM.company_id == v.c.company_id,
            NewsChunkORM.created_at >= v.c.start_date,
            case(
                (v.c.end_date.isnot(None), NewsChunkORM.created_at <= v.c.end_date),
                else_=literal(True),  # 종료 날짜가 없으면 조건 무시
            ),
        )

        # 코사인 거리 계산 및 유사도 점수 변환
        # pgvector의 cosine_distance는 0~2 범위의 값을 반환 (0: 동일, 2: 완전 반대)
        # 1 - cosine_distance로 변환하여 0~1 범위의 유사도 점수로 만듦 (1: 동일, 0: 완전 반대)
        dist = NewsChunkORM.vector.cosine_distance(cast(v.c.qvec, PG_Vector(1536)))
        sim = (literal(1.0) - dist).label("similarity_score")

        # 회사별로 유사도 순위를 매기는 서브쿼리
        # ROW_NUMBER() 윈도우 함수를 사용하여 각 회사별로 유사도가 높은 순서대로 순위를 매김
        ranked = (
            select(
                NewsChunkORM.id,
                NewsChunkORM.company_id,
                NewsChunkORM.title,
                NewsChunkORM.contents,
                sim,  # 유사도 점수
                func.row_number()
                .over(
                    partition_by=NewsChunkORM.company_id,  # 회사별로 파티션 분할
                    order_by=dist.asc(),  # 거리가 가까운 순서대로 (유사도가 높은 순서)
                )
                .label("rn"),  # 순위 번호
            )
            .select_from(
                v.join(NewsChunkORM, date_pred)
            )  # VALUES 테이블과 뉴스 테이블을 날짜 조건으로 조인
            .where(
                sim >= context.similarity_threshold
            )  # 최소 유사도 임계값 이상만 선택
            .subquery("ranked")
        )

        # 최종 결과 쿼리: 회사별로 제한된 개수만큼 선택하고 유사도 내림차순으로 정렬
        final_stmt = (
            select(
                ranked.c.id,
                ranked.c.company_id,
                ranked.c.title,
                ranked.c.contents,
                ranked.c.similarity_score,
            )
            .where(ranked.c.rn <= context.limit_per_query)  # 회사당 최대 개수 제한
            .order_by(ranked.c.similarity_score.desc())  # 유사도 높은 순서대로 정렬
        )

        # 비동기 세션을 사용하여 쿼리 실행
        async with self.session_manager as session:
            result = await session.execute(final_stmt)
            rows = result.fetchall()

        # 결과를 회사별로 그룹화하여 반환
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
