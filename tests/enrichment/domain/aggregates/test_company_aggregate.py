from datetime import date
from uuid import uuid4

import pytest

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.vos.metrics import (
    Finance,
    Investment,
    MAU,
    MonthlyMetrics,
    Organization,
    Patent,
)


class TestCompanyAggregateGetSummary:
    """CompanyAggregate.get_summary 메서드 테스트"""

    @pytest.fixture
    def company_id(self):
        """테스트용 회사 ID"""
        return uuid4()

    @pytest.fixture
    def basic_company(self, company_id):
        """기본 회사 정보"""
        return Company(
            id=company_id,
            external_id="TEST001",
            name="테스트 회사",
            name_en="Test Company",
            industry=["IT", "소프트웨어"],
            tags=["tech", "스타트업"],
            founded_date=date(2020, 1, 1),
            employee_count=100,
            stage="Series A",
            business_description="혁신적인 핀테크 회사",
            ipo_date=None,
            total_investment=5000000000,
            origin_file_path="/test/path.json",
        )

    @pytest.fixture
    def company_aliases(self, company_id):
        """회사 별칭들"""
        return [
            CompanyAlias(
                company_id=company_id,
                alias="테스트 회사",
                alias_type="name",
                id=1,
            ),
            CompanyAlias(
                company_id=company_id,
                alias="Test Company",
                alias_type="name_en",
                id=2,
            ),
            CompanyAlias(
                company_id=company_id,
                alias="TestPay",
                alias_type="product",
                id=3,
            ),
        ]

    @pytest.fixture
    def full_metrics_snapshots(self, company_id):
        """완전한 메트릭 스냅샷 데이터 (최신순)"""
        return [
            # 최신 스냅샷 (2024년)
            CompanyMetricsSnapshot(
                id=2,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[
                        MAU(
                            product_id="P001",
                            product_name="TestPay",
                            value=1000000,
                            date=date(2024, 1, 1),
                            growthRate=20.5,
                        ),
                        MAU(
                            product_id="P002",
                            product_name="TestWallet",
                            value=500000,
                            date=date(2024, 1, 1),
                            growthRate=15.0,
                        ),
                    ],
                    patents=[
                        Patent(
                            level="A+",
                            title="혁신적인 결제 기술",
                            date=date(2024, 1, 1),
                        ),
                        Patent(
                            level="A",
                            title="보안 알고리즘",
                            date=date(2024, 1, 1),
                        ),
                    ],
                    finance=[
                        Finance(
                            year=2024,
                            profit=10000000000,
                            operatingProfit=8000000000,
                            netProfit=6000000000,
                        ),
                    ],
                    investments=[
                        Investment(
                            level="Series B",
                            date=date(2024, 1, 1),
                            amount=2000000000,
                            investors=["VC Fund A", "Angel Investor B"],
                        ),
                    ],
                    organizations=[
                        Organization(
                            name="본사",
                            date=date(2024, 1, 1),
                            people_count=150,
                            growth_rate=25.0,
                        ),
                    ],
                ),
            ),
            # 이전 스냅샷 (2022년)
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2022, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[
                        MAU(
                            product_id="P001",
                            product_name="TestPay",
                            value=800000,
                            date=date(2022, 1, 1),
                            growthRate=None,
                        ),
                    ],
                    patents=[
                        Patent(
                            level="B+",
                            title="기본 결제 시스템",
                            date=date(2022, 1, 1),
                        ),
                    ],
                    finance=[
                        Finance(
                            year=2022,
                            profit=5000000000,
                            operatingProfit=4000000000,
                            netProfit=3000000000,
                        ),
                    ],
                    investments=[
                        Investment(
                            level="Series A",
                            date=date(2022, 1, 1),
                            amount=1000000000,
                            investors=["VC Fund A"],
                        ),
                    ],
                    organizations=[
                        Organization(
                            name="본사",
                            date=date(2022, 1, 1),
                            people_count=120,
                            growth_rate=10.0,
                        ),
                    ],
                ),
            ),
        ]

    @pytest.fixture
    def empty_metrics_snapshots(self, company_id):
        """빈 메트릭 스냅샷"""
        return [
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[],
                    patents=[],
                    finance=[],
                    investments=[],
                    organizations=[],
                ),
            ),
        ]

    def test_get_summary_with_full_data(
        self, basic_company, company_aliases, full_metrics_snapshots
    ):
        """완전한 데이터를 가진 회사의 요약 정보 생성 테스트"""
        # Given
        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=full_metrics_snapshots,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # 기본 회사 정보 검증
        assert summary.name == "테스트 회사"
        assert summary.name_en == "Test Company"
        assert summary.industry == ["IT", "소프트웨어"]
        assert summary.tags == ["tech", "스타트업"]
        assert summary.stage == "Series A"
        assert summary.business_description == "혁신적인 핀테크 회사"
        assert summary.founded_date == date(2020, 1, 1)
        assert summary.ipo_date is None
        assert summary.company_age_years is not None
        assert summary.is_startup is True

        # 별칭 정보 검증 (중복 제거 확인)
        expected_aliases = {"테스트 회사", "Test Company", "TestPay"}
        assert set(summary.aliases) == expected_aliases

        # 메트릭 요약 정보 검증
        metrics = summary.metrics_summary
        
        # 조직 정보 (최신 값과 성장률)
        assert metrics.people_count == 150
        assert metrics.people_growth_rate == 25.0  # (150-120)/120 * 100

        # 재무 정보 (최신 값과 성장률)
        assert metrics.profit == 10000000000
        assert metrics.net_profit == 6000000000
        assert metrics.profit_growth_rate == 100.0  # (10B-5B)/5B * 100
        assert metrics.net_profit_growth_rate == 100.0  # (6B-3B)/3B * 100

        # 투자 정보 (총합)
        assert metrics.investment_amount == 3000000000  # 2B + 1B
        assert set(metrics.investors) == {"VC Fund A", "Angel Investor B"}

        # 특허 정보 (중복 제거됨)
        assert len(metrics.patents) == 3
        patent_titles = {p.title for p in metrics.patents}
        assert "혁신적인 결제 기술" in patent_titles
        assert "보안 알고리즘" in patent_titles
        assert "기본 결제 시스템" in patent_titles

        # MAU 정보 (최신 데이터만)
        assert len(metrics.maus) == 2
        mau_products = {m.product_name: m for m in metrics.maus}
        assert "TestPay" in mau_products
        assert "TestWallet" in mau_products
        assert mau_products["TestPay"].value == 1000000
        assert mau_products["TestPay"].growth_rate == 20.5
        assert mau_products["TestWallet"].value == 500000
        assert mau_products["TestWallet"].growth_rate == 15.0

    def test_get_summary_with_empty_metrics(
        self, basic_company, company_aliases, empty_metrics_snapshots
    ):
        """빈 메트릭 데이터를 가진 회사의 요약 정보 생성 테스트"""
        # Given
        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=empty_metrics_snapshots,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # 기본 회사 정보는 유지됨
        assert summary.name == "테스트 회사"
        assert summary.name_en == "Test Company"

        # 빈 메트릭 요약 정보 검증
        metrics = summary.metrics_summary
        assert metrics.people_count == 0
        assert metrics.people_growth_rate == 0.0
        assert metrics.profit == 0
        assert metrics.net_profit == 0
        assert metrics.profit_growth_rate == 0.0
        assert metrics.net_profit_growth_rate == 0.0
        assert metrics.investment_amount == 0
        assert metrics.investors == []
        assert metrics.patents == []
        assert metrics.maus == []

    def test_get_summary_with_no_metrics_snapshots(self, basic_company, company_aliases):
        """메트릭 스냅샷이 없는 회사의 요약 정보 생성 테스트"""
        # Given
        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=[],
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # 기본 회사 정보는 유지됨
        assert summary.name == "테스트 회사"
        
        # 빈 메트릭 요약 정보가 반환됨
        metrics = summary.metrics_summary
        assert metrics.people_count == 0
        assert metrics.people_growth_rate == 0.0
        assert metrics.profit == 0
        assert metrics.net_profit == 0
        assert metrics.profit_growth_rate == 0.0
        assert metrics.net_profit_growth_rate == 0.0
        assert metrics.investment_amount == 0
        assert metrics.investors == []
        assert metrics.patents == []
        assert metrics.maus == []

    def test_get_summary_with_single_snapshot(self, basic_company, company_aliases, company_id):
        """단일 스냅샷만 있는 경우 성장률 계산 테스트"""
        # Given
        single_snapshot = [
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[],
                    patents=[],
                    finance=[
                        Finance(
                            year=2024,
                            profit=1000000000,
                            operatingProfit=800000000,
                            netProfit=600000000,
                        ),
                    ],
                    investments=[],
                    organizations=[
                        Organization(
                            name="본사",
                            date=date(2024, 1, 1),
                            people_count=100,
                            growth_rate=0.0,
                        ),
                    ],
                ),
            ),
        ]

        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=single_snapshot,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # 성장률은 0.0이어야 함 (비교할 이전 데이터가 없음)
        metrics = summary.metrics_summary
        assert metrics.people_count == 100
        assert metrics.people_growth_rate == 0.0
        assert metrics.profit == 1000000000
        assert metrics.profit_growth_rate == 0.0
        assert metrics.net_profit_growth_rate == 0.0

    def test_get_summary_with_duplicate_aliases(self, basic_company, company_id):
        """중복된 별칭이 있는 경우 중복 제거 테스트"""
        # Given
        duplicate_aliases = [
            CompanyAlias(
                company_id=company_id,
                alias="테스트 회사",
                alias_type="name",
                id=1,
            ),
            CompanyAlias(
                company_id=company_id,
                alias="테스트 회사",  # 중복
                alias_type="name",
                id=2,
            ),
            CompanyAlias(
                company_id=company_id,
                alias="TestPay",
                alias_type="product",
                id=3,
            ),
        ]

        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=duplicate_aliases,
            company_metrics_snapshots=[],
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # 중복 제거 확인
        expected_aliases = {"테스트 회사", "TestPay"}
        assert set(summary.aliases) == expected_aliases
        assert len(summary.aliases) == 2

    def test_get_summary_with_none_values_in_finance(self, basic_company, company_aliases, company_id):
        """Finance의 netProfit이 None인 경우 처리 테스트"""
        # Given
        snapshots_with_none_netprofit = [
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[],
                    patents=[],
                    finance=[
                        Finance(
                            year=2024,
                            profit=1000000000,
                            operatingProfit=800000000,
                            netProfit=None,  # None 값
                        ),
                    ],
                    investments=[],
                    organizations=[],
                ),
            ),
        ]

        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=snapshots_with_none_netprofit,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # None 값이 0으로 처리되어야 함
        metrics = summary.metrics_summary
        assert metrics.net_profit == 0

    def test_get_summary_with_mau_none_growth_rate(self, basic_company, company_aliases, company_id):
        """MAU의 growthRate이 None인 경우 처리 테스트"""
        # Given
        snapshots_with_none_growth_rate = [
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[
                        MAU(
                            product_id="P001",
                            product_name="TestPay",
                            value=1000000,
                            date=date(2024, 1, 1),
                            growthRate=None,  # None 값
                        ),
                    ],
                    patents=[],
                    finance=[],
                    investments=[],
                    organizations=[],
                ),
            ),
        ]

        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=snapshots_with_none_growth_rate,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # None 값이 0.0으로 처리되어야 함
        metrics = summary.metrics_summary
        assert len(metrics.maus) == 1
        assert metrics.maus[0].growth_rate == 0.0

    def test_get_summary_duplicate_patents(self, basic_company, company_aliases, company_id):
        """중복 특허 제거 테스트 (level + title 조합으로 구분)"""
        # Given
        snapshots_with_duplicate_patents = [
            CompanyMetricsSnapshot(
                id=1,
                company_id=company_id,
                reference_date=date(2024, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[],
                    patents=[
                        Patent(
                            level="A",
                            title="결제 기술",
                            date=date(2024, 1, 1),
                        ),
                        Patent(
                            level="A",
                            title="결제 기술",  # 완전히 동일한 특허
                            date=date(2023, 1, 1),  # 날짜는 다름
                        ),
                        Patent(
                            level="B",
                            title="결제 기술",  # 제목은 같지만 레벨이 다름
                            date=date(2024, 1, 1),
                        ),
                    ],
                    finance=[],
                    investments=[],
                    organizations=[],
                ),
            ),
        ]

        aggregate = CompanyAggregate(
            company=basic_company,
            company_aliases=company_aliases,
            company_metrics_snapshots=snapshots_with_duplicate_patents,
        )

        # When
        summary = aggregate.get_summary()

        # Then
        # level + title 조합으로 중복 제거되어 2개만 남아야 함
        metrics = summary.metrics_summary
        assert len(metrics.patents) == 2
        
        patent_keys = {(p.level, p.title) for p in metrics.patents}
        expected_keys = {("A", "결제 기술"), ("B", "결제 기술")}
        assert patent_keys == expected_keys