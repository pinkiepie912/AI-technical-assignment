from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from enrichment.domain.vos.metrics import MonthlyMetrics

__all__ = ["CompanyMetricsSnapshot", "CompanyMetricSnapshotCreateParams"]


class CompanyMetricSnapshotCreateParams(BaseModel):
    company_id: UUID
    reference_date: date
    metrics: MonthlyMetrics

    model_config = ConfigDict(frozen=True)


class CompanyMetricsSnapshot(BaseModel):
    company_id: UUID
    reference_date: date
    metrics: MonthlyMetrics
    id: Optional[int] = None

    @staticmethod
    def of(params: CompanyMetricSnapshotCreateParams) -> CompanyMetricsSnapshot:
        snapshot = CompanyMetricsSnapshot(
            company_id=params.company_id,
            reference_date=params.reference_date,
            metrics=params.metrics,
            id=None,
        )
        return snapshot
