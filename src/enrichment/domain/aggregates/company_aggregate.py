from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from enrichment.domain.dtos.summary import (
    CompanySummary,
    MAUSummary,
    MetricsSummary,
    PatentSummary,
)
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.vos.metrics import MAU


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

    def get_summary(self) -> CompanySummary:
        """
        LLM에게 제공할 회사 요약 정보 생성
        재직기간 동안의 회사 메트릭 정보와 기본 회사 정보를 포함하여
        LLM이 회사에 대한 종합적인 이해를 할 수 있도록 구성

        Returns:
            CompanySummary: LLM용 회사 요약 정보
        """
        # 기본 회사 정보
        company = self.company

        # 회사 별칭 목록 생성 (중복 제거)
        aliases = list(set(alias.alias for alias in self.company_aliases))

        # 메트릭 요약 정보 생성
        metrics_summary = self._get_metrics_summary()

        return CompanySummary(
            name=company.name,
            name_en=company.name_en,
            industry=company.industry,
            tags=company.tags,
            stage=company.stage,
            business_description=company.business_description,
            founded_date=company.founded_date,
            ipo_date=company.ipo_date,
            company_age_years=company.get_company_age_years(),
            is_startup=company.is_startup(),
            aliases=aliases,
            metrics_summary=metrics_summary,
        )

    def _get_metrics_summary(self) -> MetricsSummary:
        """
        회사 메트릭 스냅샷 데이터를 기반으로 메트릭 요약 정보 생성

        성능 최적화를 위해:
        - 단일 순회로 모든 메트릭 데이터 수집
        - 필요한 데이터만 추출하여 메모리 사용량 최소화
        - 조기 반환으로 불필요한 연산 방지

        Returns:
            MetricsSummary: 회사의 메트릭 요약 정보
        """
        if not self.company_metrics_snapshots:
            return self._create_empty_metrics_summary()

        # 최신 순으로 정렬된 스냅샷에서 첫 번째(최신)와 마지막(최초) 추출
        latest_snapshot = self.company_metrics_snapshots[0]
        earliest_snapshot = self.company_metrics_snapshots[-1]

        # 조직 정보 (직원 수 및 성장률)
        people_count, people_growth_rate = self._calculate_people_metrics(
            latest_snapshot, earliest_snapshot
        )

        # 재무 정보 (매출, 순이익 및 성장률)
        profit, net_profit, profit_growth_rate, net_profit_growth_rate = (
            self._calculate_finance_metrics(latest_snapshot, earliest_snapshot)
        )

        # 투자 정보 (총 투자 금액 및 투자자 목록)
        investment_amount, investors = self._calculate_investment_metrics()

        # 특허 정보
        patents = self._calculate_patent_metrics()

        # MAU 정보 (제품별)
        maus = self._calculate_mau_metrics(latest_snapshot)

        return MetricsSummary(
            people_count=people_count,
            people_growth_rate=people_growth_rate,
            profit=profit,
            net_profit=net_profit,
            profit_growth_rate=profit_growth_rate,
            net_profit_growth_rate=net_profit_growth_rate,
            investment_amount=investment_amount,
            investors=investors,
            patents=patents,
            maus=maus,
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
            patents=[],
            maus=[],
        )

    def _calculate_people_metrics(
        self, latest_snapshot, earliest_snapshot
    ) -> tuple[int, float]:
        """조직 메트릭 계산: 직원 수와 성장률"""
        latest_people_count = 0
        earliest_people_count = 0

        # 최신 직원 수 추출
        if latest_snapshot.metrics.organizations:
            latest_people_count = latest_snapshot.metrics.organizations[-1].people_count

        # 최초 직원 수 추출 (성장률 계산용)
        if (
            len(self.company_metrics_snapshots) > 1
            and earliest_snapshot.metrics.organizations
        ):
            earliest_people_count = earliest_snapshot.metrics.organizations[
                -1
            ].people_count

        # 성장률 계산
        people_growth_rate = self._calculate_growth_rate(
            earliest_people_count, latest_people_count
        )

        return latest_people_count, people_growth_rate

    def _calculate_finance_metrics(
        self, latest_snapshot, earliest_snapshot
    ) -> tuple[int, int, float, float]:
        """재무 메트릭 계산: 매출, 순이익 및 성장률"""
        latest_profit = 0
        latest_net_profit = 0
        earliest_profit = 0
        earliest_net_profit = 0

        # 최신 재무 데이터 추출
        if latest_snapshot.metrics.finance:
            latest_finance = latest_snapshot.metrics.finance[-1]
            latest_profit = latest_finance.profit
            latest_net_profit = latest_finance.netProfit or 0

        # 최초 재무 데이터 추출 (성장률 계산용)
        if (
            len(self.company_metrics_snapshots) > 1
            and earliest_snapshot.metrics.finance
        ):
            earliest_finance = earliest_snapshot.metrics.finance[-1]
            earliest_profit = earliest_finance.profit
            earliest_net_profit = earliest_finance.netProfit or 0

        # 성장률 계산
        profit_growth_rate = self._calculate_growth_rate(earliest_profit, latest_profit)
        net_profit_growth_rate = self._calculate_growth_rate(
            earliest_net_profit, latest_net_profit
        )

        return (
            latest_profit,
            latest_net_profit,
            profit_growth_rate,
            net_profit_growth_rate,
        )

    def _calculate_investment_metrics(self) -> tuple[int, List[str]]:
        """투자 메트릭 계산: 총 투자 금액과 투자자 목록"""
        total_investment_amount = 0
        all_investors = set()

        # 모든 스냅샷의 투자 데이터를 순회하여 집계
        for snapshot in self.company_metrics_snapshots:
            for investment in snapshot.metrics.investments:
                total_investment_amount += investment.amount
                all_investors.update(investment.investors)

        return total_investment_amount, list(all_investors)

    def _calculate_patent_metrics(self) -> List[PatentSummary]:
        """특허 메트릭 계산: 모든 특허 목록"""
        patents = []

        # 중복 제거를 위한 특허 추적 (level + title 조합으로 구분)
        seen_patents = set()

        for snapshot in self.company_metrics_snapshots:
            for patent in snapshot.metrics.patents:
                patent_key = (patent.level, patent.title)
                if patent_key not in seen_patents:
                    seen_patents.add(patent_key)
                    patents.append(
                        PatentSummary(level=patent.level, title=patent.title)
                    )

        return patents

    def _calculate_mau_metrics(self, latest_snapshot) -> List[MAUSummary]:
        """MAU 메트릭 계산: 제품별 최신 MAU 데이터"""
        mau_by_product: Dict[str, MAU] = {}

        # 최신 스냅샷에서 제품별 MAU 추출
        for mau in latest_snapshot.metrics.mau:
            # 동일 제품의 경우 최신 데이터로 덮어쓰기
            mau_by_product[mau.product_name] = mau

        # MAUSummary 형태로 변환
        return [
            MAUSummary(
                product_name=mau.product_name,
                value=mau.value,
                growth_rate=mau.growthRate or 0.0,
            )
            for mau in mau_by_product.values()
        ]

    def _calculate_growth_rate(self, initial_value: int, final_value: int) -> float:
        """성장률 계산 헬퍼 메서드

        Args:
            initial_value: 초기 값
            final_value: 최종 값

        Returns:
            float: 성장률 (퍼센트 단위)
        """
        if initial_value == 0:
            return 0.0

        return ((final_value - initial_value) / initial_value) * 100.0
