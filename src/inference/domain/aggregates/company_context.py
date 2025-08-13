from dataclasses import dataclass

from inference.domain.entities.company import Company
from inference.domain.entities.company_metrics import MetricsSummary


@dataclass
class CompanyContext:
    # 기본 회사 정보
    company: Company

    # 재직기간 동안의 메트릭 요약 정보
    metrics: MetricsSummary
