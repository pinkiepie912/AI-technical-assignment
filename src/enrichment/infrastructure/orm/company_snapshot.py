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
    __tablename__ = "company_metrics_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)

    reference_date: Mapped[date] = mapped_column(Date, index=True)

    metrics: Mapped[Dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default="{}",
    )

    company: Mapped["Company"] = relationship("Company", back_populates="snapshots")

    __table_args__ = (Index("idx_company_date", "company_id", "reference_date"),)
