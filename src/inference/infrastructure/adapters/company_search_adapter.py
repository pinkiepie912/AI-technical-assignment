from typing import List

from enrichment.application.ports.company_search_service_port import (
    CompanySearchParam,
    CompanySearchServicePort,
)
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.entities.company import Company
from inference.domain.entities.company_metrics import (
    MAUSummary,
    MetricsSummary,
    PatentSummary,
)
from inference.domain.repositories.company_context_search_port import (
    CompanyContextSearchPort,
    CompanySearchContextParam,
)


class CompanyContextSearchAdapter(CompanyContextSearchPort):
    def __init__(self, company_search_service: CompanySearchServicePort):
        self.company_search_service = company_search_service

    async def search(
        self, params: List[CompanySearchContextParam]
    ) -> List[CompanyContext]:
        companies = await self.company_search_service.get_companies(
            params=[
                CompanySearchParam(
                    alias=param.alias,
                    start_date=param.start_date,
                    end_date=param.end_date,
                )
                for param in params
            ]
        )

        return [self._get_summary(company) for company in companies]

    def _get_summary(self, info: CompanyAggregate) -> CompanyContext:
        """
        CompanyContext 생성

        """
        return CompanyContext(
            company=Company(
                id=info.company.id,
                name=info.company.name,
                name_en=info.company.name_en,
                industry=info.company.industry,
                tags=info.company.tags,
                stage=info.company.stage,
                business_description=info.company.business_description,
                founded_date=info.company.founded_date,
                ipo_date=info.company.ipo_date,
                aliases=[row.alias for row in info.company_aliases],
            ),
            metrics=self._get_metrics_summary(info),
        )

    def _get_metrics_summary(self, info: CompanyAggregate) -> MetricsSummary:
        """
        회사 메트릭 스냅샷 데이터를 기반으로 메트릭 요약 정보 생성

        Returns:
            MetricsSummary: 회사의 메트릭 요약 정보
        """
        if not info.company_metrics_snapshots:
            return self._create_empty_metrics_summary()

        # 조직 정보 (직원 수 및 성장률)
        people_count, people_growth_rate = info.calculate_people_metrics()

        # 재무 정보 (매출, 순이익 및 성장률)
        profit, net_profit, profit_growth_rate, net_profit_growth_rate = (
            info.calculate_finance_metrics()
        )

        # 투자 정보 (총 투자 금액 및 투자자 목록)
        investment_amount, investors, levels = info.calculate_investment_metrics()

        # 특허 정보
        patents = info.calculate_patent_metrics()

        # MAU 정보 (제품별)
        maus = info.calculate_mau_metrics()

        return MetricsSummary(
            people_count=people_count,
            people_growth_rate=people_growth_rate,
            profit=profit,
            net_profit=net_profit,
            profit_growth_rate=profit_growth_rate,
            net_profit_growth_rate=net_profit_growth_rate,
            investment_amount=investment_amount,
            investors=investors,
            levels=levels,
            patents=[PatentSummary(level=row[0], title=row[1]) for row in patents],
            maus=[
                MAUSummary(product_name=row[0], value=row[1], growth_rate=row[2])
                for row in maus
            ],
        )

    def _create_empty_metrics_summary(self) -> MetricsSummary:
        """빈 메트릭 요약 정보 생성"""
        return MetricsSummary(
            people_count=0,
            people_growth_rate=0.0,
            profit=0,
            net_profit=0,
            profit_growth_rate=0.0,
            net_profit_growth_rate=0.0,
            investment_amount=0,
            investors=[],
            levels=[],
            patents=[],
            maus=[],
        )
