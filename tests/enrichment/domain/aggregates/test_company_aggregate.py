"""Test cases for CompanyAggregate"""

from datetime import date
from uuid import UUID

import pytest

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company, CompanyCreateParams
from enrichment.domain.entities.company_alias import (
    CompanyAlias,
    CompanyAliasCreateParams,
)
from enrichment.domain.entities.company_metrics_snapshot import (
    CompanyMetricSnapshotCreateParams,
    CompanyMetricsSnapshot,
)
from enrichment.domain.vos.metrics import (
    MAU,
    Finance,
    Investment,
    MonthlyMetrics,
    Organization,
    Patent,
)


class TestCompanyAggregate:
    def test_create_aggregate_minimal(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        # Company 생성
        company_params = CompanyCreateParams(
            external_id="test_company", name="테스트회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id  # ID 설정

        # 빈 리스트들
        company_aliases = []
        company_metrics_snapshots = []

        aggregate = CompanyAggregate.of(
            company=company,
            company_aliases=company_aliases,
            company_metrics_snapshots=company_metrics_snapshots,
        )

        assert aggregate.company == company
        assert aggregate.company_aliases == []
        assert aggregate.company_metrics_snapshots == []

    def test_create_aggregate_with_aliases(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        # Company 생성
        company_params = CompanyCreateParams(
            external_id="test_company", name="네이버", employee_count=3000
        )
        company = Company.of(company_params)
        company.id = company_id

        # Aliases 생성
        alias_params1 = CompanyAliasCreateParams(
            company_id=company_id, alias="NAVER", alias_type="company_name"
        )
        alias_params2 = CompanyAliasCreateParams(
            company_id=company_id, alias="네이버 블로그", alias_type="product_name"
        )

        company_aliases = [
            CompanyAlias.of(alias_params1),
            CompanyAlias.of(alias_params2),
        ]

        aggregate = CompanyAggregate.of(
            company=company,
            company_aliases=company_aliases,
            company_metrics_snapshots=[],
        )

        assert aggregate.company.name == "네이버"
        assert len(aggregate.company_aliases) == 2
        assert aggregate.company_aliases[0].alias == "NAVER"
        assert aggregate.company_aliases[1].alias == "네이버 블로그"

    def test_calculate_people_metrics_no_snapshots(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="테스트회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        with pytest.raises(ValueError, match="No company metrics snapshots available"):
            aggregate.calculate_people_metrics()

    def test_calculate_people_metrics_single_snapshot(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        # Company 생성
        company_params = CompanyCreateParams(
            external_id="test_company", name="테스트회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # 조직 데이터가 있는 스냅샷 생성
        organization = Organization(
            name="전체", date=date(2023, 12, 31), people_count=150, growth_rate=15.0
        )

        metrics = MonthlyMetrics(
            mau=[], patents=[], finance=[], investments=[], organizations=[organization]
        )

        snapshot_params = CompanyMetricSnapshotCreateParams(
            company_id=company_id, reference_date=date(2023, 12, 31), metrics=metrics
        )
        snapshot = CompanyMetricsSnapshot.of(snapshot_params)

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[snapshot]
        )

        people_count, growth_rate = aggregate.calculate_people_metrics()

        assert people_count == 150
        assert growth_rate == 0.0  # 단일 스냅샷이므로 성장률은 0

    def test_calculate_people_metrics_multiple_snapshots(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        # Company 생성
        company_params = CompanyCreateParams(
            external_id="test_company", name="성장회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # 첫 번째 스냅샷 (과거)
        old_organization = Organization(
            name="전체", date=date(2023, 1, 31), people_count=100, growth_rate=0.0
        )
        old_metrics = MonthlyMetrics(
            mau=[],
            patents=[],
            finance=[],
            investments=[],
            organizations=[old_organization],
        )
        old_snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 1, 31),
                metrics=old_metrics,
            )
        )

        # 두 번째 스냅샷 (최신)
        new_organization = Organization(
            name="전체", date=date(2023, 12, 31), people_count=200, growth_rate=20.0
        )
        new_metrics = MonthlyMetrics(
            mau=[],
            patents=[],
            finance=[],
            investments=[],
            organizations=[new_organization],
        )
        new_snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=new_metrics,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company,
            company_aliases=[],
            company_metrics_snapshots=[new_snapshot, old_snapshot],  # 최신이 첫 번째
        )

        people_count, growth_rate = aggregate.calculate_people_metrics()

        assert people_count == 200
        assert growth_rate == 100.0  # (200-100)/100 * 100 = 100%

    def test_calculate_finance_metrics_single_snapshot(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="재무회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # 재무 데이터가 있는 스냅샷 생성
        finance = Finance(
            year=2023, profit=1000000000, operatingProfit=800000000, netProfit=600000000
        )

        metrics = MonthlyMetrics(
            mau=[], patents=[], finance=[finance], investments=[], organizations=[]
        )

        snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=metrics,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[snapshot]
        )

        profit, net_profit, profit_growth, net_profit_growth = (
            aggregate.calculate_finance_metrics()
        )

        assert profit == 1000000000
        assert net_profit == 600000000
        assert profit_growth == 0.0
        assert net_profit_growth == 0.0

    def test_calculate_investment_metrics(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="투자회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # 투자 데이터가 있는 스냅샷들 생성
        investment1 = Investment(
            level="Seed",
            date=date(2023, 3, 15),
            amount=1000000000,
            investors=["벤처캐피탈A", "엔젤투자자B"],
        )

        investment2 = Investment(
            level="Series A",
            date=date(2023, 9, 20),
            amount=5000000000,
            investors=["벤처캐피탈A", "투자회사C"],
        )

        metrics1 = MonthlyMetrics(
            mau=[], patents=[], finance=[], investments=[investment1], organizations=[]
        )
        metrics2 = MonthlyMetrics(
            mau=[], patents=[], finance=[], investments=[investment2], organizations=[]
        )

        snapshot1 = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 3, 31),
                metrics=metrics1,
            )
        )
        snapshot2 = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 9, 30),
                metrics=metrics2,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company,
            company_aliases=[],
            company_metrics_snapshots=[snapshot2, snapshot1],
        )

        total_amount, investors, levels = aggregate.calculate_investment_metrics()

        assert total_amount == 6000000000  # 1B + 5B
        assert set(investors) == {"벤처캐피탈A", "엔젤투자자B", "투자회사C"}
        assert set(levels) == {"Seed", "Series A"}

    def test_calculate_patent_metrics(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="특허회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # 특허 데이터가 있는 스냅샷 생성
        patent1 = Patent(level="국내특허", title="AI 알고리즘", date=date(2023, 6, 15))
        patent2 = Patent(
            level="국제특허", title="데이터 처리 방법", date=date(2023, 9, 20)
        )

        metrics = MonthlyMetrics(
            mau=[],
            patents=[patent1, patent2],
            finance=[],
            investments=[],
            organizations=[],
        )

        snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=metrics,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[snapshot]
        )

        patents = aggregate.calculate_patent_metrics()

        assert len(patents) == 2
        assert ("국내특허", "AI 알고리즘") in patents
        assert ("국제특허", "데이터 처리 방법") in patents

    def test_calculate_mau_metrics(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="서비스회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        # MAU 데이터가 있는 스냅샷 생성
        mau1 = MAU(
            product_id="service_1",
            product_name="메인서비스",
            value=1000000,
            date=date(2023, 12, 31),
            growthRate=15.5,
        )
        mau2 = MAU(
            product_id="service_2",
            product_name="서브서비스",
            value=500000,
            date=date(2023, 12, 31),
            growthRate=25.0,
        )

        metrics = MonthlyMetrics(
            mau=[mau1, mau2], patents=[], finance=[], investments=[], organizations=[]
        )

        snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=metrics,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[snapshot]
        )

        mau_metrics = aggregate.calculate_mau_metrics()

        assert len(mau_metrics) == 2
        assert ("메인서비스", 1000000, 15.5) in mau_metrics
        assert ("서브서비스", 500000, 25.0) in mau_metrics

    def test_calculate_growth_rate_helper(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        company_params = CompanyCreateParams(
            external_id="test_company", name="테스트회사", employee_count=100
        )
        company = Company.of(company_params)
        company.id = company_id

        aggregate = CompanyAggregate.of(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        # 정상적인 성장률 계산
        assert aggregate._calculate_growth_rate(100, 150) == 50.0
        assert aggregate._calculate_growth_rate(200, 100) == -50.0

        # 초기값이 0인 경우
        assert aggregate._calculate_growth_rate(0, 100) == 0.0

        # 동일한 값인 경우
        assert aggregate._calculate_growth_rate(100, 100) == 0.0

    def test_comprehensive_aggregate(self):
        """모든 구성 요소가 포함된 종합 테스트"""
        company_id = UUID("12345678-1234-5678-9abc-123456789012")

        # Company
        company_params = CompanyCreateParams(
            external_id="comprehensive_company",
            name="종합회사",
            name_en="Comprehensive Company",
            industry=["Technology", "Finance"],
            tags=["innovation", "growth"],
            employee_count=500,
            stage="Series B",
            business_description="종합 기술 회사",
            founded_date=date(2020, 1, 15),
            ipo_date=date(2023, 6, 30),
            total_investment=10000000000,
            origin_file_path="/data/comprehensive.json",
        )
        company = Company.of(company_params)
        company.id = company_id

        # Aliases
        aliases = [
            CompanyAlias.of(
                CompanyAliasCreateParams(
                    company_id=company_id, alias="CompCorp", alias_type="company_name"
                )
            ),
            CompanyAlias.of(
                CompanyAliasCreateParams(
                    company_id=company_id, alias="CompApp", alias_type="product_name"
                )
            ),
        ]

        # Comprehensive metrics
        comprehensive_metrics = MonthlyMetrics(
            mau=[
                MAU(
                    product_id="p1",
                    product_name="앱A",
                    value=2000000,
                    date=date(2023, 12, 31),
                    growthRate=20.0,
                )
            ],
            patents=[
                Patent(level="국제특허", title="혁신기술", date=date(2023, 8, 15))
            ],
            finance=[
                Finance(
                    year=2023,
                    profit=20000000000,
                    operatingProfit=15000000000,
                    netProfit=10000000000,
                )
            ],
            investments=[
                Investment(
                    level="Series B",
                    date=date(2023, 5, 10),
                    amount=8000000000,
                    investors=["메가VC"],
                )
            ],
            organizations=[
                Organization(
                    name="전체",
                    date=date(2023, 12, 31),
                    people_count=500,
                    growth_rate=25.0,
                )
            ],
        )

        snapshot = CompanyMetricsSnapshot.of(
            CompanyMetricSnapshotCreateParams(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=comprehensive_metrics,
            )
        )

        aggregate = CompanyAggregate.of(
            company=company,
            company_aliases=aliases,
            company_metrics_snapshots=[snapshot],
        )

        # 모든 메트릭 검증
        assert aggregate.company.name == "종합회사"
        assert len(aggregate.company_aliases) == 2
        assert len(aggregate.company_metrics_snapshots) == 1

        # 각종 메트릭 계산 검증
        people_count, _ = aggregate.calculate_people_metrics()
        assert people_count == 500

        profit, net_profit, _, _ = aggregate.calculate_finance_metrics()
        assert profit == 20000000000
        assert net_profit == 10000000000

        total_investment, investors, levels = aggregate.calculate_investment_metrics()
        assert total_investment == 8000000000
        assert "메가VC" in investors

        patents = aggregate.calculate_patent_metrics()
        assert len(patents) == 1
        assert ("국제특허", "혁신기술") in patents

        mau_metrics = aggregate.calculate_mau_metrics()
        assert len(mau_metrics) == 1
        assert ("앱A", 2000000, 20.0) in mau_metrics

