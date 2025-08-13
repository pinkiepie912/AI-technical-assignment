import pytest
from uuid import uuid4
from datetime import date

from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.entities.company import Company
from inference.domain.entities.company_metrics import MetricsSummary


class TestCompanyContext:
    @pytest.fixture
    def sample_company(self):
        return Company(
            id=uuid4(),
            name="Test Company",
            name_en="Test Company Inc.",
            industry=["IT"],
            tags=["Software"],
            stage="Seed",
            business_description="A tech company",
            founded_date=date(2020, 1, 1),
            ipo_date=None,
            aliases=["TestCo"]
        )

    @pytest.fixture
    def sample_metrics_summary(self):
        return MetricsSummary(
            people_count=100,
            people_growth_rate=0.1,
            profit=1000,
            net_profit=500,
            profit_growth_rate=0.05,
            net_profit_growth_rate=0.03,
            investment_amount=1000000,
            investors=["Investor A"],
            levels=["Seed"],
            patents=[],
            maus=[]
        )

    def test_company_context_creation(self, sample_company, sample_metrics_summary):
        company_context = CompanyContext(
            company=sample_company,
            metrics=sample_metrics_summary
        )

        assert company_context.company == sample_company
        assert company_context.metrics == sample_metrics_summary
