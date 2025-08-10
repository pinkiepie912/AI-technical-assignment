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
    investment_total: Optional[int] = None
    stage: Optional[str] = None
    business_description: Optional[str] = None
    founded_date: Optional[date] = None
    ipo_date: Optional[date] = None
    total_investment: Optional[int] = None
    origin_file_path: str = ""

    model_config = ConfigDict(frozen=True)


class Company(BaseModel):
    id: UUID
    external_id: str
    name: str
    name_en: Optional[str]
    industry: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    founded_date: Optional[date]
    employee_count: Optional[int]
    investment_total: Optional[int]
    stage: Optional[str]
    business_description: Optional[str]
    ipo_date: Optional[date]
    total_investment: Optional[int]
    origin_file_path: str

    @staticmethod
    def of(params: CompanyCreateParams) -> Company:
        return Company(
            id=UUID(int=0),  # Default UUID
            external_id=params.external_id,
            name=params.name,
            name_en=params.name_en,
            industry=params.industry,
            tags=params.tags,
            founded_date=params.founded_date,
            employee_count=params.employee_count,
            investment_total=params.investment_total,
            stage=params.stage,
            business_description=params.business_description,
            ipo_date=params.ipo_date,
            total_investment=params.total_investment,
            origin_file_path=params.origin_file_path,
        )

    def get_company_age_years(self) -> Optional[int]:
        if not self.founded_date:
            return None

        today = date.today()
        return today.year - self.founded_date.year

    def is_startup(self) -> bool:
        """Startup is defined as a company founded within the last 10 years."""
        age = self.get_company_age_years()
        return age is not None and age <= 10
