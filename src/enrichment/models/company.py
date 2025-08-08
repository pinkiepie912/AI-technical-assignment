from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime, date

from sqlalchemy import BigInteger, DateTime, String, Integer, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

from db.model import Base

if TYPE_CHECKING:
    from .company_alias import CompanyAlias
    from .company_snapshot import CompanySnapshot


__all__ = ["Company"]


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    name_en: Mapped[str] = mapped_column(
        String(64), default="", server_default="", index=True
    )

    current_employee_count: Mapped[int] = mapped_column(Integer, nullable=True)
    current_investment_total: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )
    current_stage: Mapped[str] = mapped_column(String(20), nullable=True)

    business_description: Mapped[str] = mapped_column(Text, nullable=True)

    founded_date: Mapped[date] = mapped_column(Date, nullable=True)
    ipo_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    total_investment: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )

    data: Mapped[Dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default="{}",
    )

    aliases: Mapped[List["CompanyAlias"]] = relationship(
        "CompanyAlias", back_populates="company"
    )
    snapshots: Mapped[List["CompanySnapshot"]] = relationship(
        "CompanySnapshot", back_populates="company"
    )
