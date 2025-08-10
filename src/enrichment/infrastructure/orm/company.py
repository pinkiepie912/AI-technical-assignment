from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import ARRAY, BigInteger, Date, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model import Base

if TYPE_CHECKING:
    from .company_alias import CompanyAlias
    from .company_snapshot import CompanyMetricsSnapshot


__all__ = ["Company"]


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    external_id: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(64), index=True)

    name_en: Mapped[str] = mapped_column(
        String(64), default="", server_default="", index=True
    )

    biz_categories: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, server_default=text("'{}'")
    )

    biz_tags: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, server_default=text("'{}'")
    )

    biz_description: Mapped[str] = mapped_column(
        String(255), default="", server_default=""
    )

    stage: Mapped[str] = mapped_column(String(32), default="", server_default="")

    total_investment: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )

    founded_date: Mapped[date] = mapped_column(Date)

    employee_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    ipo_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    total_investment: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )

    origin_file_path: Mapped[str] = mapped_column(
        String(255), default="", server_default=""
    )

    aliases: Mapped[List["CompanyAlias"]] = relationship(
        "CompanyAlias", back_populates="company"
    )

    snapshots: Mapped[List["CompanyMetricsSnapshot"]] = relationship(
        "CompanyMetricsSnapshot", back_populates="company"
    )
