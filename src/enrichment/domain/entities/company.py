from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Company", "CompanyCreateParams"]


class CompanyCreateParams(BaseModel):
    external_id: str
    name: str
    name_en: Optional[str] = None
    industry: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    employee_count: int
    stage: Optional[str] = None
    business_description: Optional[str] = None
    founded_date: Optional[date] = None
    ipo_date: Optional[date] = None
    total_investment: Optional[int] = None
    origin_file_path: str = ""

    model_config = ConfigDict(frozen=True)


class Company(BaseModel):
    """
    회사 도메인 엔티티 - 회사의 기본 정보와 비즈니스 로직을 담당
    CompanyCreateParams를 통해 생성되며, CompanyAggregate의 핵심 구성 요소
    """

    id: UUID  # 회사 고유 식별자
    external_id: str  # 외부 시스템 회사 ID
    name: str  # 회사명 (한국어)
    name_en: Optional[str]  # 회사명 (영어)
    industry: List[str] = Field(default_factory=list)  # 사업 분야 목록
    tags: List[str] = Field(default_factory=list)  # 비즈니스 태그 목록
    founded_date: Optional[date]  # 창립일
    employee_count: Optional[int]  # 직원 수
    stage: Optional[str]  # 투자 단계
    business_description: Optional[str]  # 사업 설명
    ipo_date: Optional[date]  # IPO 날짜
    total_investment: Optional[int]  # 총 투자 금액 (중복 필드)
    origin_file_path: str  # 원본 데이터 파일 경로

    @staticmethod
    def of(params: CompanyCreateParams) -> Company:
        return Company(
            id=UUID(int=0),  # 기본 UUID (실제로는 별도 할당)
            external_id=params.external_id,
            name=params.name,
            name_en=params.name_en,
            industry=params.industry,
            tags=params.tags,
            founded_date=params.founded_date,
            employee_count=params.employee_count,
            stage=params.stage,
            business_description=params.business_description,
            ipo_date=params.ipo_date,
            total_investment=params.total_investment,
            origin_file_path=params.origin_file_path,
        )
