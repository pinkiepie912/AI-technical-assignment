from __future__ import annotations

from typing import TYPE_CHECKING, Dict
from uuid import UUID
from datetime import date

from sqlalchemy import Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

from db.model import Base

if TYPE_CHECKING:
    from .company import Company

__all__ = ["CompanySnapshot"]


class CompanySnapshot(Base):
    __tablename__ = "company_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)
    reference_date: Mapped[date] = mapped_column(Date, index=True)
    llm_context: Mapped[Dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default="{}",
    )
    origin_metrics: Mapped[Dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default="{}",
    )

    company: Mapped["Company"] = relationship("Company", back_populates="snapshots")

    __table_args__ = (Index("idx_company_date", "company_id", "reference_date"),)
