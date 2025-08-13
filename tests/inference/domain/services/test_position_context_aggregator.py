from datetime import date
from uuid import UUID

import pytest

from inference.controllers.dtos.talent_infer import (
    DateModel,
    Position,
    StartEndDate,
    TalentProfile,
)
from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.aggregates.talent_career_journey import TalentCareerJourney
from inference.domain.entities.company import Company
from inference.domain.entities.company_metrics import MetricsSummary
from inference.domain.entities.news_chunk import NewsChunk
from inference.domain.services.position_context_aggregator import (
    PositionContextAggregator,
)


class TestPositionContextAggregator:
    @pytest.fixture
    def sample_talent_profile(self):
        return TalentProfile(
            firstName="John",
            lastName="Doe",
            headline="Software Engineer",
            summary="Experienced engineer.",
            photoUrl="http://example.com/photo.jpg",
            linkedinUrl="https://www.linkedin.com/in/johndoe",
            industryName="IT",
            positions=[
                Position(
                    companyName="Company A",
                    title="Engineer",
                    companyLocation="Seoul",
                    companyLogo="logoA.png",
                    description="",
                    startEndDate=StartEndDate(
                        start=DateModel(year=2020, month=1),
                        end=DateModel(year=2021, month=1),
                    ),
                ),
                Position(
                    companyName="Company B",
                    title="Senior Engineer",
                    companyLocation="Busan",
                    companyLogo="logoB.png",
                    description="",
                    startEndDate=StartEndDate(
                        start=DateModel(year=2021, month=2), end=None
                    ),
                ),
            ],
        )

    @pytest.fixture
    def sample_company_context_a(self):
        return CompanyContext(
            company=Company(
                id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
                name="Company A",
                name_en="Company A Inc.",
                industry=["IT"],
                tags=["Software"],
                stage="Seed",
                business_description="",
                founded_date=date(2019, 1, 1),
                ipo_date=None,
                aliases=["Company A", "CompA"],
            ),
            metrics=MetricsSummary(
                people_count=100,
                people_growth_rate=0.1,
                profit=1000,
                net_profit=500,
                profit_growth_rate=0.05,
                net_profit_growth_rate=0.03,
                investment_amount=1000000,
                investors=["Inv A"],
                levels=["Seed"],
                patents=[],
                maus=[],
            ),
        )

    @pytest.fixture
    def sample_company_context_b(self):
        return CompanyContext(
            company=Company(
                id=UUID("b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"),
                name="Company B",
                name_en="Company B Inc.",
                industry=["Finance"],
                tags=["Fintech"],
                stage="Series A",
                business_description="",
                founded_date=date(2018, 1, 1),
                ipo_date=None,
                aliases=["Company B", "CompB"],
            ),
            metrics=MetricsSummary(
                people_count=200,
                people_growth_rate=0.2,
                profit=2000,
                net_profit=1000,
                profit_growth_rate=0.1,
                net_profit_growth_rate=0.06,
                investment_amount=2000000,
                investors=["Inv B"],
                levels=["Series A"],
                patents=[],
                maus=[],
            ),
        )

    @pytest.fixture
    def sample_news_chunk_a(self):
        return NewsChunk(
            id=1,
            company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
            title="News A for Company A",
            contents="Content A",
        )

    @pytest.fixture
    def sample_news_chunk_b(self):
        return NewsChunk(
            id=2,
            company_id=UUID("b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"),
            title="News B for Company B",
            contents="Content B",
        )

    @pytest.mark.asyncio
    async def test_aggregate_career_journey_success(
        self,
        sample_talent_profile,
        sample_company_context_a,
        sample_company_context_b,
        sample_news_chunk_a,
        sample_news_chunk_b,
    ):
        # Arrange
        company_contexts = [sample_company_context_a, sample_company_context_b]
        news_by_companies = {
            sample_company_context_a.company.id: [sample_news_chunk_a],
            sample_company_context_b.company.id: [sample_news_chunk_b],
        }

        # Act
        journey = PositionContextAggregator.aggregate_career_journey(
            sample_talent_profile, company_contexts, news_by_companies
        )

        # Assert
        assert isinstance(journey, TalentCareerJourney)
        assert journey.talent_profile == sample_talent_profile
        assert len(journey.position_contexts) == 2

        # Check first position context (Company A)
        pos_ctx_a = journey.position_contexts[0]
        assert pos_ctx_a.position.companyName == "Company A"
        assert pos_ctx_a.company_context == sample_company_context_a
        assert len(pos_ctx_a.related_news) == 1
        assert pos_ctx_a.related_news[0] == sample_news_chunk_a

        # Check second position context (Company B)
        pos_ctx_b = journey.position_contexts[1]
        assert pos_ctx_b.position.companyName == "Company B"
        assert pos_ctx_b.company_context == sample_company_context_b
        assert len(pos_ctx_b.related_news) == 1
        assert pos_ctx_b.related_news[0] == sample_news_chunk_b

    @pytest.mark.asyncio
    async def test_aggregate_career_journey_no_company_context(
        self, sample_talent_profile, sample_news_chunk_a
    ):
        # Arrange
        company_contexts = []
        news_by_companies = {sample_news_chunk_a.company_id: [sample_news_chunk_a]}

        # Act
        journey = PositionContextAggregator.aggregate_career_journey(
            sample_talent_profile, company_contexts, news_by_companies
        )

        # Assert
        assert isinstance(journey, TalentCareerJourney)
        assert len(journey.position_contexts) == 2
        assert journey.position_contexts[0].company_context is None
        assert journey.position_contexts[0].related_news == []
        assert journey.position_contexts[1].company_context is None
        assert journey.position_contexts[1].related_news == []

    @pytest.mark.asyncio
    async def test_aggregate_career_journey_no_news(
        self, sample_talent_profile, sample_company_context_a, sample_company_context_b
    ):
        # Arrange
        company_contexts = [sample_company_context_a, sample_company_context_b]
        news_by_companies = {}

        # Act
        journey = PositionContextAggregator.aggregate_career_journey(
            sample_talent_profile, company_contexts, news_by_companies
        )

        # Assert
        assert isinstance(journey, TalentCareerJourney)
        assert len(journey.position_contexts) == 2
        assert journey.position_contexts[0].company_context == sample_company_context_a
        assert journey.position_contexts[0].related_news == []
        assert journey.position_contexts[1].company_context == sample_company_context_b
        assert journey.position_contexts[1].related_news == []

    def test_build_company_context_map(
        self, sample_company_context_a, sample_company_context_b
    ):
        # Arrange
        company_contexts = [sample_company_context_a, sample_company_context_b]

        # Act
        company_map = PositionContextAggregator._build_company_context_map(
            company_contexts
        )

        # Assert
        assert len(company_map) == 4  # Company A, CompA, Company B, CompB
        assert company_map["company a"] == sample_company_context_a
        assert company_map["compa"] == sample_company_context_a
        assert company_map["company b"] == sample_company_context_b
        assert company_map["compb"] == sample_company_context_b

    def test_find_company_context_success(self, sample_company_context_a):
        # Arrange
        company_context_map = {"company a": sample_company_context_a}
        position = Position(
            companyName="Company A",
            title="Engineer",
            companyLocation="Seoul",
            companyLogo="logoA.png",
            description="",
            startEndDate=StartEndDate(
                start=DateModel(year=2020, month=1), end=DateModel(year=2021, month=1)
            ),
        )

        # Act
        found_context = PositionContextAggregator._find_company_context(
            position, company_context_map
        )

        # Assert
        assert found_context == sample_company_context_a

    def test_find_company_context_not_found(self, sample_company_context_a):
        # Arrange
        company_context_map = {"company a": sample_company_context_a}
        position = Position(
            companyName="NonExistent Company",
            title="Engineer",
            companyLocation="Seoul",
            companyLogo="logoA.png",
            description="",
            startEndDate=StartEndDate(
                start=DateModel(year=2020, month=1), end=DateModel(year=2021, month=1)
            ),
        )

        # Act
        found_context = PositionContextAggregator._find_company_context(
            position, company_context_map
        )

        # Assert
        assert found_context is None

    def test_find_related_news_with_context(
        self, sample_company_context_a, sample_news_chunk_a
    ):
        # Arrange
        news_by_companies = {sample_company_context_a.company.id: [sample_news_chunk_a]}

        # Act
        related_news = PositionContextAggregator._find_related_news(
            sample_company_context_a, news_by_companies
        )

        # Assert
        assert len(related_news) == 1
        assert related_news[0] == sample_news_chunk_a

    def test_find_related_news_no_context(self, sample_news_chunk_a):
        # Arrange
        news_by_companies = {sample_news_chunk_a.company_id: [sample_news_chunk_a]}

        # Act
        related_news = PositionContextAggregator._find_related_news(
            None, news_by_companies
        )

        # Assert
        assert related_news == []

    def test_find_related_news_no_matching_news(self, sample_company_context_a):
        # Arrange
        news_by_companies = {}

        # Act
        related_news = PositionContextAggregator._find_related_news(
            sample_company_context_a, news_by_companies
        )

        # Assert
        assert related_news == []
