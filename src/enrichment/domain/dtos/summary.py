from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PatentSummary(BaseModel):
    level: str
    title: str


class MAUSummary(BaseModel):
    product_name: str
    value: int
    growth_rate: float


class MetricsSummary(BaseModel):
    people_count: int
    people_growth_rate: float

    profit: int
    net_profit: int
    profit_growth_rate: float
    net_profit_growth_rate: float

    investment_amount: int
    investors: List[str]

    patents: List[PatentSummary]
    maus: List[MAUSummary]

    model_config = ConfigDict(frozen=True)


class CompanySummary(BaseModel):
    """
    LLM에게 제공할 회사 요약 정보
    재직기간 동안의 회사 정보와 기본 회사 정보를 포함
    """

    # 기본 회사 정보
    name: str  # 회사명 (한국어)
    name_en: Optional[str]  # 회사명 (영어)
    industry: List[str]  # 사업 분야 목록
    tags: List[str]  # 비즈니스 태그 목록
    stage: Optional[str]  # 투자 단계 (예: Series A, Series B)
    business_description: Optional[str]  # 사업 설명

    # 회사 설립 및 상장 정보
    founded_date: Optional[date]  # 창립일
    ipo_date: Optional[date]  # IPO 날짜
    company_age_years: Optional[int]  # 회사 연령 (년)
    is_startup: bool  # 스타트업 여부

    # 회사 별칭 정보 (식별을 위한 추가 정보)
    aliases: List[str]  # 회사를 식별할 수 있는 모든 이름들 (회사명, 제품명 등)

    # 재직기간 동안의 메트릭 요약 정보
    metrics_summary: MetricsSummary  # 시계열 데이터 요약

    model_config = ConfigDict(frozen=True)
