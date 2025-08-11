from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Dict
from uuid import UUID

from sqlalchemy import BigInteger, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model import Base

if TYPE_CHECKING:
    from .company import Company

__all__ = ["CompanyMetricsSnapshot"]


class CompanyMetricsSnapshot(Base):
    """
    회사 메트릭 스냅샷 테이블 - 회사의 시계열 데이터를 월별로 저장
    Reader에서 MAU, 투자, 특허, 재무, 조직 데이터를 MonthlyMetrics 형태로 수집하여 JSONB 형태로 저장됨
    """

    __tablename__ = "company_metrics_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)

    # 기준 날짜: 메트릭 데이터의 기준이 되는 월 (매월 1일로 통일)
    reference_date: Mapped[date] = mapped_column(Date, index=True)

    # 메트릭 데이터: MonthlyMetrics 객체를 JSONB 형태로 저장
    # reference_date(해당 월 1일 기준)에 해당하는 회사의 메트릭을 저장한다.
    # MAU, 투자, 특허, 재무, 조직 정보 등의 시계열 데이터 포함
    metrics: Mapped[Dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default="{}",
    )

    # 관계: 소속 회사 정보
    company: Mapped["Company"] = relationship("Company", back_populates="snapshots")

    # 복합 인덱스: 회사별 날짜 순서로 빠른 조회를 위한 인덱스
    __table_args__ = (Index("idx_company_date", "company_id", "reference_date"),)
