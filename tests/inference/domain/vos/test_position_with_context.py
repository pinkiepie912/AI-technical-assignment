import pytest
from datetime import date
from uuid import uuid4

from inference.controllers.dtos.talent_infer import Position, StartEndDate, DateModel
from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.entities.company import Company
from inference.domain.entities.company_metrics import MetricsSummary
from inference.domain.entities.news_chunk import NewsChunk
from inference.domain.vos.position_with_context import PositionWithContext


class TestPositionWithContext:
    @pytest.fixture
    def sample_position(self):
        return Position(
            companyName="Test Company",
            title="Software Engineer",
            companyLocation="Seoul",
            companyLogo="logo.png",
            description="Developed software.",
            startEndDate=StartEndDate(start=DateModel(year=2020, month=1), end=DateModel(year=2021, month=12))
        )

    @pytest.fixture
    def sample_company_context(self):
        return CompanyContext(
            company=Company(
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
            ),
            metrics=MetricsSummary(
                people_count=100, people_growth_rate=0.1, profit=1000, net_profit=500,
                profit_growth_rate=0.05, net_profit_growth_rate=0.03, investment_amount=1000000,
                investors=["Investor A"], levels=["Seed"], patents=[], maus=[]
            )
        )

    @pytest.fixture
    def sample_news_chunk(self):
        return NewsChunk(
            id=1,
            company_id=uuid4(),
            title="Sample News",
            contents="News content"
        )

    def test_position_with_context_creation(self, sample_position, sample_company_context, sample_news_chunk):
        pwc = PositionWithContext(
            position=sample_position,
            company_context=sample_company_context,
            related_news=[sample_news_chunk]
        )
        assert pwc.position == sample_position
        assert pwc.company_context == sample_company_context
        assert pwc.related_news == [sample_news_chunk]

    def test_get_chronological_order_key_with_month(self, sample_position, sample_company_context, sample_news_chunk):
        pwc = PositionWithContext(
            position=sample_position,
            company_context=sample_company_context,
            related_news=[sample_news_chunk]
        )
        assert pwc.get_chronological_order_key() == (2020, 1)

    def test_get_chronological_order_key_without_month(self, sample_company_context, sample_news_chunk):
        position_without_month = Position(
            companyName="Another Company",
            title="Developer",
            companyLocation="Busan",
            companyLogo="logo2.png",
            description="Coding.",
            startEndDate=StartEndDate(start=DateModel(year=2019, month=None), end=DateModel(year=2020, month=None))
        )
        pwc = PositionWithContext(
            position=position_without_month,
            company_context=sample_company_context,
            related_news=[sample_news_chunk]
        )
        assert pwc.get_chronological_order_key() == (2019, 1)

    def test_position_with_context_no_company_context(self, sample_position, sample_news_chunk):
        pwc = PositionWithContext(
            position=sample_position,
            company_context=None,
            related_news=[sample_news_chunk]
        )
        assert pwc.company_context is None

    def test_position_with_context_no_related_news(self, sample_position, sample_company_context):
        pwc = PositionWithContext(
            position=sample_position,
            company_context=sample_company_context,
            related_news=[]
        )
        assert pwc.related_news == []
