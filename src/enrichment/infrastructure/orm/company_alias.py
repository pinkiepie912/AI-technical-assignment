from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model import Base

if TYPE_CHECKING:
    from .company import Company

__all__ = ["CompanyAlias"]


class CompanyAlias(Base):
    __tablename__ = "company_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)

    alias: Mapped[str] = mapped_column(String(100), index=True)

    alias_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    company: Mapped["Company"] = relationship("Company", back_populates="aliases")
