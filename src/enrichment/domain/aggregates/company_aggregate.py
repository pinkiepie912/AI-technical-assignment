from __future__ import annotations
from dataclasses import dataclass
from typing import List

from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot


@dataclass
class CompanyAggregate:
    company: Company
    company_aliases: List[CompanyAlias]
    company_metrics_snapshots: List[CompanyMetricsSnapshot]

    @staticmethod
    def of(
        company: Company,
        company_aliases: List[CompanyAlias],
        company_metrics_snapshots: List[CompanyMetricsSnapshot]
    ) -> CompanyAggregate:
        return CompanyAggregate(
            company=company,
            company_aliases=company_aliases,
            company_metrics_snapshots=company_metrics_snapshots,
        )
