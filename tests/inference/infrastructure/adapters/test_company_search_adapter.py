import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from uuid import UUID, uuid4

from enrichment.application.ports.company_search_service_port import CompanySearchParam
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company as EnrichmentCompany
from enrichment.domain.entities.company_alias import CompanyAlias as EnrichmentCompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot as EnrichmentCompanyMetricsSnapshot
from enrichment.domain.vos.metrics import MonthlyMetrics, MAU, Patent, Finance, Investment, Organization

from inference.domain.repositories.company_context_search_port import CompanySearchContextParam
from inference.infrastructure.adapters.company_search_adapter import CompanyContextSearchAdapter
from inference.domain.entities.company_metrics import MetricsSummary, PatentSummary, MAUSummary


class TestCompanyContextSearchAdapter:
    @pytest.fixture
    def mock_company_search_service(self):
        return AsyncMock()

    @pytest.fixture
    def adapter(self, mock_company_search_service):
        return CompanyContextSearchAdapter(company_search_service=mock_company_search_service)

    @pytest.fixture
    def sample_enrichment_company_aggregate(self):
        company_id = uuid4()
        company = EnrichmentCompany(
            id=company_id,
            external_id="test-external-id",
            name="테스트회사",
            name_en="Test Company",
            industry=["IT", "Software"],
            tags=["startup", "ai"],
            founded_date=date(2020, 1, 15),
            employee_count=100,
            stage="Series A",
            business_description="AI 기반 서비스 회사",
            ipo_date=date(2023, 6, 30),
            total_investment=5000000000,
            origin_file_path="/data/company.json"
        )
        aliases = [
            EnrichmentCompanyAlias(company_id=company_id, alias="테스트회사", alias_type="company_name", id=1),
            EnrichmentCompanyAlias(company_id=company_id, alias="Test Company", alias_type="company_name", id=2)
        ]
        metrics = MonthlyMetrics(
            mau=[MAU(date=date(2023, 1, 1), product_id="prodA", product_name="productA", value=100, growthRate=0.1)],
            patents=[Patent(date=date(2023, 1, 1), level="level1", title="patent1")],
            finance=[Finance(year=2023, profit=1000, operatingProfit=500, netProfit=500)],
            investments=[Investment(date=date(2023, 1, 1), amount=10000, investors=["investorA"], level="seed")],
            organizations=[Organization(date=date(2023, 1, 1), name="orgA", people_count=100, growth_rate=0.1)]
        )
        snapshots = [
            EnrichmentCompanyMetricsSnapshot(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=MonthlyMetrics(
                    mau=[MAU(date=date(2023, 1, 1), product_id="prodA", product_name="productA", value=100, growthRate=0.1)],
                    patents=[Patent(date=date(2023, 1, 1), level="level1", title="patent1")],
                    finance=[Finance(year=2023, profit=1000, operatingProfit=500, netProfit=500)],
                    investments=[Investment(date=date(2023, 1, 1), amount=10000, investors=["investorA"], level="seed")],
                    organizations=[Organization(date=date(2023, 1, 1), name="orgA", people_count=100, growth_rate=0.1)]
                ),
                id=2
            ),
            EnrichmentCompanyMetricsSnapshot(
                company_id=company_id,
                reference_date=date(2023, 1, 1),
                metrics=MonthlyMetrics(
                    mau=[], patents=[], finance=[], investments=[],
                    organizations=[Organization(date=date(2023, 1, 1), name="orgA", people_count=50, growth_rate=0.0)]
                ),
                id=1
            )
        ]
        return CompanyAggregate(
            company=company,
            company_aliases=aliases,
            company_metrics_snapshots=snapshots
        )

    @pytest.mark.asyncio
    async def test_search_success(self, adapter, mock_company_search_service, sample_enrichment_company_aggregate):
        # Arrange
        search_params = [
            CompanySearchContextParam(alias="테스트회사", start_date=date(2023, 1, 1), end_date=date(2023, 12, 31))
        ]
        mock_company_search_service.get_companies.return_value = [sample_enrichment_company_aggregate]

        # Act
        result = await adapter.search(search_params)

        # Assert
        mock_company_search_service.get_companies.assert_called_once_with(
            params=[CompanySearchParam(alias="테스트회사", start_date=date(2023, 1, 1), end_date=date(2023, 12, 31))]
        )
        assert len(result) == 1
        company_context = result[0]
        assert company_context.company.name == "테스트회사"
        assert company_context.company.aliases == ["테스트회사", "Test Company"]
        assert company_context.metrics.people_count == 100
        assert company_context.metrics.profit == 1000
        assert company_context.metrics.investment_amount == 10000
        assert len(company_context.metrics.patents) == 1
        assert company_context.metrics.patents[0].title == "patent1"
        assert len(company_context.metrics.maus) == 1
        assert company_context.metrics.maus[0].product_name == "productA"

    @pytest.mark.asyncio
    async def test_search_no_results(self, adapter, mock_company_search_service):
        # Arrange
        search_params = [
            CompanySearchContextParam(alias="없는회사", start_date=date(2023, 1, 1), end_date=date(2023, 12, 31))
        ]
        mock_company_search_service.get_companies.return_value = []

        # Act
        result = await adapter.search(search_params)

        # Assert
        mock_company_search_service.get_companies.assert_called_once()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_empty_params(self, adapter, mock_company_search_service):
        # Arrange
        search_params = []
        mock_company_search_service.get_companies.return_value = []

        # Act
        result = await adapter.search(search_params)

        # Assert
        mock_company_search_service.get_companies.assert_called_once_with(params=[])
        assert len(result) == 0

    def test_get_summary(self, adapter, sample_enrichment_company_aggregate):
        # Act
        summary = adapter._get_summary(sample_enrichment_company_aggregate)

        # Assert
        assert summary.company.id == sample_enrichment_company_aggregate.company.id
        assert summary.company.name == "테스트회사"
        assert summary.company.aliases == ["테스트회사", "Test Company"]
        assert isinstance(summary.metrics, MetricsSummary)

    def test_get_metrics_summary_with_data(self, adapter, sample_enrichment_company_aggregate):
        # Act
        metrics_summary = adapter._get_metrics_summary(sample_enrichment_company_aggregate)

        # Assert
        assert metrics_summary.people_count == 100
        assert metrics_summary.people_growth_rate == 100.0
        assert metrics_summary.profit == 1000
        assert metrics_summary.net_profit == 500
        assert metrics_summary.profit_growth_rate == 0.0 # Default value, as not calculated in aggregate
        assert metrics_summary.net_profit_growth_rate == 0.0 # Default value
        assert metrics_summary.investment_amount == 10000
        assert metrics_summary.investors == ["investorA"]
        assert metrics_summary.levels == ["seed"]
        assert len(metrics_summary.patents) == 1
        assert metrics_summary.patents[0].level == "level1"
        assert metrics_summary.patents[0].title == "patent1"
        assert len(metrics_summary.maus) == 1
        assert metrics_summary.maus[0].product_name == "productA"
        assert metrics_summary.maus[0].value == 100
        assert metrics_summary.maus[0].growth_rate == 0.1

    def test_get_metrics_summary_no_snapshots(self, adapter):
        # Arrange
        company_id = uuid4()
        company = EnrichmentCompany(
            id=company_id,
            external_id="test",
            name="Test",
            name_en="Test Company",
            industry=[],
            tags=[],
            founded_date=date(2020, 1, 1),
            employee_count=0,
            stage="",
            business_description="",
            ipo_date=None,
            total_investment=0,
            origin_file_path=""
        )
        aggregate_no_snapshots = CompanyAggregate(
            company=company,
            company_aliases=[],
            company_metrics_snapshots=[]
        )

        # Act
        metrics_summary = adapter._get_metrics_summary(aggregate_no_snapshots)

        # Assert
        assert metrics_summary.people_count == 0
        assert metrics_summary.people_growth_rate == 0.0
        assert metrics_summary.profit == 0
        assert metrics_summary.net_profit == 0
        assert metrics_summary.profit_growth_rate == 0.0
        assert metrics_summary.net_profit_growth_rate == 0.0
        assert metrics_summary.investment_amount == 0
        assert metrics_summary.investors == []
        assert metrics_summary.levels == []
        assert metrics_summary.patents == []
        assert metrics_summary.maus == []

    def test_create_empty_metrics_summary(self, adapter):
        # Act
        empty_summary = adapter._create_empty_metrics_summary()

        # Assert
        assert empty_summary.people_count == 0
        assert empty_summary.people_growth_rate == 0.0
        assert empty_summary.profit == 0
        assert empty_summary.net_profit == 0
        assert empty_summary.profit_growth_rate == 0.0
        assert empty_summary.net_profit_growth_rate == 0.0
        assert empty_summary.investment_amount == 0
        assert empty_summary.investors == []
        assert empty_summary.levels == []
        assert empty_summary.patents == []
        assert empty_summary.maus == []
