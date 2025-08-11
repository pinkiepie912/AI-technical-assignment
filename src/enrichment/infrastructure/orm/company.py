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
    """
    회사 정보를 저장하는 메인 테이블
    ForestOfHyuksinReader에서 JSON 데이터를 파싱하여 CompanyAggregate로 생성되고,
    CompanyRepository의 save 메서드를 통해 데이터베이스에 저장됨
    """

    __tablename__ = "companies"

    # 기본키: UUID 형태의 회사 고유 식별자
    id: Mapped[UUID] = mapped_column(primary_key=True)

    # 외부 시스템에서 제공하는 회사 ID (예: Forest of Hyuksin의 회사 ID)
    external_id: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, index=True
    )

    # 회사명 (한국어)
    name: Mapped[str] = mapped_column(String(64), index=True)

    # 회사명 (영어)
    name_en: Mapped[str] = mapped_column(
        String(64), default="", server_default="", index=True
    )

    # 사업 카테고리 목록 (배열 형태로 저장)
    biz_categories: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, server_default=text("'{}'")
    )

    # 비즈니스 태그 목록 (배열 형태로 저장)
    biz_tags: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, server_default=text("'{}'")
    )

    # 사업 설명/소개
    biz_description: Mapped[str] = mapped_column(
        String(255), default="", server_default=""
    )

    # 투자 단계 (예: Series A, Series B 등)
    stage: Mapped[str] = mapped_column(String(32), default="", server_default="")

    # 창립일
    founded_date: Mapped[date] = mapped_column(Date)

    # 직원 수
    employee_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # IPO 날짜 (상장일)
    ipo_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 총 투자 금액 (중복 필드 - 데이터 정합성 개선 필요)
    total_investment: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )

    # 원본 데이터 파일 경로
    origin_file_path: Mapped[str] = mapped_column(
        String(255), default="", server_default=""
    )

    # 관계: 회사 별칭 목록 (회사명, 제품명 등)
    aliases: Mapped[List["CompanyAlias"]] = relationship(
        "CompanyAlias", back_populates="company"
    )

    # 관계: 회사 메트릭 스냅샷 목록 (시계열 데이터)
    snapshots: Mapped[List["CompanyMetricsSnapshot"]] = relationship(
        "CompanyMetricsSnapshot", back_populates="company"
    )
