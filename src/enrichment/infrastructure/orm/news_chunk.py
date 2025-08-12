from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model import Base

if TYPE_CHECKING:
    from .company import Company


__all__ = ["NewsChunk"]


class NewsChunk(Base):
    """
    뉴스 기사의 청크를 저장하는 테이블
    """

    __tablename__ = "news_chunks"

    # 기본키: 청크 ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 외래키: 회사 ID (뉴스가 속한 회사)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)

    # 뉴스 제목
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # 청크 내용
    contents: Mapped[str] = mapped_column(Text, nullable=False)

    # 청크 내용을 1536차원 벡터로 저장(text-embedding-3-small dim)
    vector: Mapped[Vector] = mapped_column(Vector(1536), nullable=False)

    # 원본 뉴스 링크
    link: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # 뉴스 기사 생성 날짜 (부모 뉴스와 동일)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # 관계: 회사 정보
    company: Mapped["Company"] = relationship("Company", back_populates="news_chunks")

    __table_args__ = (
        Index(
            "idx_chunk_hnsw",
            "vector",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"vector": "vector_cosine_ops"},
        ),
        # 인덱스: created_at과 company_id를 조합한 인덱스
        Index(
            "idx_news_chunk_created_at_company_id",
            "created_at",
            "company_id",
            unique=False,
        ),
    )
