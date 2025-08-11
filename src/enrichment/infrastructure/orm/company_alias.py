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
    """
    회사 별칭 테이블 - 회사명, 제품명 등 회사를 식별할 수 있는 다양한 이름들을 저장
    """

    __tablename__ = "company_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), index=True)

    # 별칭: 회사를 식별할 수 있는 이름 (회사명, 제품명 등)
    alias: Mapped[str] = mapped_column(String(100), index=True)

    # 별칭 타입: 별칭의 종류 구분 (예: "name" - 회사명, "product" - 제품명)
    alias_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # 관계: 소속 회사 정보
    company: Mapped["Company"] = relationship("Company", back_populates="aliases")
