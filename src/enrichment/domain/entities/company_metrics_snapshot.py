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
    """
    회사 메트릭 스냅샷 도메인 엔티티 - 회사의 시계열 데이터를 관리
    MAU, 투자, 특허, 재무, 조직 정보 등을 월별로 저장하며 CompanyAggregate의 구성 요소
    """

    company_id: UUID  # 소속 회사 ID
    reference_date: date  # 메트릭 기준 날짜
    metrics: MonthlyMetrics  # 월별 메트릭 데이터
    id: Optional[int] = None  # 데이터베이스 기본키 (생성 후 할당)

    @staticmethod
    def of(params: CompanyMetricSnapshotCreateParams) -> CompanyMetricsSnapshot:
        snapshot = CompanyMetricsSnapshot(
            company_id=params.company_id,
            reference_date=params.reference_date,
            metrics=params.metrics,
            id=None,
        )
        return snapshot
