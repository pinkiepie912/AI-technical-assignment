from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .company_alias import CompanyAlias, CompanyAliasCreateParams
from .company_metrics_snapshot import (
    CompanyMetricSnapshotCreateParams,
    CompanyMetricsSnapshot,
)

__all__ = ["Company", "CompanyCreateParams"]


class CompanyCreateParams(BaseModel):
    name: str
    name_en: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    investment_total: Optional[int] = None
    stage: Optional[str] = None
    business_description: Optional[str] = None
    founded_date: Optional[date] = None
    ipo_date: Optional[date] = None
    total_investment: Optional[int] = None
    origin_file_path: str = ""

    alias_params: List[CompanyAliasCreateParams] = Field(default_factory=list)
    snapshot_params: List[CompanyMetricSnapshotCreateParams] = Field(
        default_factory=list
    )

    model_config = ConfigDict(frozen=True)


class Company(BaseModel):
    id: UUID
    name: str
    name_en: Optional[str]
    industry: Optional[str]
    founded_date: Optional[date]
    employee_count: Optional[int]
    investment_total: Optional[int]
    stage: Optional[str]
    business_description: Optional[str]
    ipo_date: Optional[date]
    total_investment: Optional[int]
    origin_file_path: str
    company_aliases: List[CompanyAlias]
    company_snapshot: List[CompanyMetricsSnapshot]

    @staticmethod
    def of(params: CompanyCreateParams) -> Company:
        return Company(
            id=UUID(int=0),  # Default UUID
            name=params.name,
            name_en=params.name_en,
            industry=params.industry,
            founded_date=params.founded_date,
            employee_count=params.employee_count,
            investment_total=params.investment_total,
            stage=params.stage,
            business_description=params.business_description,
            ipo_date=params.ipo_date,
            total_investment=params.total_investment,
            origin_file_path=params.origin_file_path,
            company_aliases=[CompanyAlias.of(p) for p in params.alias_params],
            company_snapshot=[
                CompanyMetricsSnapshot.of(p) for p in params.snapshot_params
            ],
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
