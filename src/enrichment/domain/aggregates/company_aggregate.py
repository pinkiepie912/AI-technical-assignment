from __future__ import annotations

from dataclasses import dataclass
from typing import List

from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot


@dataclass
class CompanyAggregate:
    """
    Company 애그리게이트 - DDD 패턴의 애그리게이트 루트

    구성 요소:
    - Company: 회사 기본 정보
    - CompanyAlias: 회사 별칭들 (회사명, 제품명 등)
    - CompanyMetricsSnapshot: 시계열 메트릭 데이터 (MAU, 투자, 특허 등)
    """

    company: Company  # 회사 기본 정보
    company_aliases: List[CompanyAlias]  # 회사 별칭 목록
    company_metrics_snapshots: List[CompanyMetricsSnapshot]  # 메트릭 스냅샷 목록

    @staticmethod
    def of(
        company: Company,
        company_aliases: List[CompanyAlias],
        company_metrics_snapshots: List[CompanyMetricsSnapshot],
    ) -> CompanyAggregate:
        """회사 엔티티와 관련 데이터들로부터 CompanyAggregate 생성"""
        return CompanyAggregate(
            company=company,
            company_aliases=company_aliases,
            company_metrics_snapshots=company_metrics_snapshots,
        )
