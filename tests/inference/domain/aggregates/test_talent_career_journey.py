from datetime import date
from uuid import uuid4

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
from inference.domain.vos.position_with_context import PositionWithContext


class TestTalentCareerJourney:
    @pytest.fixture
    def sample_talent_profile(self):
        return TalentProfile(
            firstName="John",
            lastName="Doe",
            headline="Software Engineer at Example Corp",
            summary="Experienced software engineer with a passion for AI.",
            photoUrl="http://example.com/photo.jpg",
            linkedinUrl="https://www.linkedin.com/in/johndoe",
            industryName="Information Technology",
            positions=[],
        )

    @pytest.fixture
    def sample_company_context(self):
        return CompanyContext(
            company=Company(
                id=uuid4(),
                name="Sample Company",
                name_en="Sample Company Inc.",
                industry=["IT"],
                tags=["Software"],
                stage="Seed",
                business_description="A tech company",
                founded_date=date(2020, 1, 1),
                ipo_date=None,
                aliases=["SampleCo"],
            ),
            metrics=MetricsSummary(
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
                maus=[],
            ),
        )

    @pytest.fixture
    def sample_news_chunk(self):
        return NewsChunk(
            id=1, company_id=uuid4(), title="Sample News", contents="News content"
        )

    @pytest.fixture
    def position_with_context_1(self, sample_company_context, sample_news_chunk):
        return PositionWithContext(
            position=Position(
                companyName="Company A",
                title="Software Engineer",
                description="Developed software",
                companyLocation="Seoul, South Korea",
                companyLogo="http://example.com/logoA.png",
                startEndDate=StartEndDate(
                    start=DateModel(year=2020, month=1),
                    end=DateModel(year=2021, month=1),
                ),
            ),
            company_context=sample_company_context,
            related_news=[sample_news_chunk],
        )

    @pytest.fixture
    def position_with_context_2(self, sample_company_context, sample_news_chunk):
        return PositionWithContext(
            position=Position(
                companyName="Company B",
                title="Senior Software Engineer",
                description="Led team",
                companyLocation="Seoul, South Korea",
                companyLogo="http://example.com/logoB.png",
                startEndDate=StartEndDate(
                    start=DateModel(year=2019, month=1),
                    end=DateModel(year=2020, month=1),
                ),
            ),
            company_context=sample_company_context,
            related_news=[sample_news_chunk],
        )

    @pytest.fixture
    def position_with_context_3(self, sample_company_context, sample_news_chunk):
        return PositionWithContext(
            position=Position(
                companyName="Company C",
                title="Staff Engineer",
                description="Mentored others",
                companyLocation="Seoul, South Korea",
                companyLogo="http://example.com/logoC.png",
                startEndDate=StartEndDate(
                    start=DateModel(year=2021, month=1), end=None
                ),
            ),
            company_context=sample_company_context,
            related_news=[sample_news_chunk],
        )

    def test_talent_career_journey_creation(
        self, sample_talent_profile, position_with_context_1
    ):
        journey = TalentCareerJourney(
            talent_profile=sample_talent_profile,
            position_contexts=[position_with_context_1],
        )
        assert journey.talent_profile == sample_talent_profile
        assert len(journey.position_contexts) == 1
        assert journey.position_contexts[0] == position_with_context_1

    def test_get_chronological_journey_sorted(
        self,
        sample_talent_profile,
        position_with_context_1,
        position_with_context_2,
        position_with_context_3,
    ):
        # Positions are intentionally out of order
        journey = TalentCareerJourney(
            talent_profile=sample_talent_profile,
            position_contexts=[
                position_with_context_1,  # Start 2020-01-01
                position_with_context_2,  # Start 2019-01-01
                position_with_context_3,  # Start 2021-01-01
            ],
        )

        sorted_journey = journey.get_chronological_journey()

        assert len(sorted_journey) == 3
        assert sorted_journey[0] == position_with_context_2  # 2019
        assert sorted_journey[1] == position_with_context_1  # 2020
        assert sorted_journey[2] == position_with_context_3  # 2021

    def test_get_chronological_journey_empty(self, sample_talent_profile):
        journey = TalentCareerJourney(
            talent_profile=sample_talent_profile, position_contexts=[]
        )
        sorted_journey = journey.get_chronological_journey()
        assert sorted_journey == []
