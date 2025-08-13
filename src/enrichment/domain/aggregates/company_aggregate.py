from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

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

    def calculate_people_metrics(self) -> Tuple[int, float]:
        """조직 메트릭 계산: 직원 수와 성장률"""

        latest_snapshot, earliest_snapshot = self._get_latest_earliest_snapshots()

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

    def calculate_finance_metrics(self) -> Tuple[int, int, float, float]:
        """재무 메트릭 계산: 매출, 순이익 및 성장률"""
        latest_snapshot, earliest_snapshot = self._get_latest_earliest_snapshots()

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

    def calculate_investment_metrics(self) -> Tuple[int, List[str], List[str]]:
        """투자 메트릭 계산: 총 투자 금액과 투자자 목록"""
        total_investment_amount = 0
        all_investors = set()
        levels = []

        # 모든 스냅샷의 투자 데이터를 순회하여 집계
        for snapshot in self.company_metrics_snapshots:
            for investment in snapshot.metrics.investments:
                total_investment_amount += investment.amount
                all_investors.update(investment.investors)
                levels.append(investment.level)

        return total_investment_amount, list(all_investors), list(levels)

    def calculate_patent_metrics(self) -> List[Tuple[str, str]]:
        """특허 메트릭 계산: 모든 특허 목록"""
        patents = []

        for snapshot in self.company_metrics_snapshots:
            for patent in snapshot.metrics.patents:
                patents.append((patent.level, patent.title))

        return patents

    def calculate_mau_metrics(self) -> List[Tuple[str, int, float]]:
        """MAU 메트릭 계산: 제품별 최신 MAU 데이터"""
        mau_by_product: Dict[str, MAU] = {}

        latest_snapshot = self.company_metrics_snapshots[0]

        # 최신 스냅샷에서 제품별 MAU 추출
        for mau in latest_snapshot.metrics.mau:
            # 동일 제품의 경우 최신 데이터로 덮어쓰기
            mau_by_product[mau.product_name] = mau

        return [
            (mau.product_name, mau.value, mau.growthRate or 0.0)
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

    def _get_latest_earliest_snapshots(
        self,
    ) -> Tuple[CompanyMetricsSnapshot, CompanyMetricsSnapshot]:
        """최신 및 최초 스냅샷 추출"""
        if not self.company_metrics_snapshots:
            raise ValueError("No company metrics snapshots available")

        latest_snapshot = self.company_metrics_snapshots[0]
        earliest_snapshot = self.company_metrics_snapshots[-1]

        return latest_snapshot, earliest_snapshot
