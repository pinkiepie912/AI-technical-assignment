from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from inference.application.services.talent_infer import TalentInference
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
from inference.domain.repositories.news_search_port import (
    NewsChunkByCompany,
)
from inference.domain.vos.openai_models import LLMModel
from inference.domain.vos.position_with_context import PositionWithContext


class TestTalentInference:
    @pytest.fixture
    def mock_company_search_adapter(self):
        return AsyncMock()

    @pytest.fixture
    def mock_news_search_adapter(self):
        return AsyncMock()

    @pytest.fixture
    def mock_llm_client(self):
        return AsyncMock()

    @pytest.fixture
    def talent_inference_service(
        self, mock_company_search_adapter, mock_news_search_adapter, mock_llm_client
    ):
        return TalentInference(
            company_search_adapter=mock_company_search_adapter,
            news_search_adapter=mock_news_search_adapter,
            llm_client=mock_llm_client,
        )

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
                    description="Developed software for Company A.",
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
                    description="Led team at Company B.",
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
    async def test_inference_success(
        self,
        talent_inference_service,
        mock_company_search_adapter,
        mock_news_search_adapter,
        mock_llm_client,
        sample_talent_profile,
        sample_company_context_a,
        sample_company_context_b,
        sample_news_chunk_a,
        sample_news_chunk_b,
    ):
        # Arrange
        mock_company_search_adapter.search.return_value = [
            sample_company_context_a,
            sample_company_context_b,
        ]
        mock_news_search_adapter.search.return_value = [
            NewsChunkByCompany(
                company_id=sample_company_context_a.company.id,
                news_chunks=[sample_news_chunk_a],
            ),
            NewsChunkByCompany(
                company_id=sample_company_context_b.company.id,
                news_chunks=[sample_news_chunk_b],
            ),
        ]
        mock_llm_client.answer.return_value = r"""```json
{"experience_tags": ["Software Development"], "skill_tags": ["Python"]}
```"""

        # Act
        result = await talent_inference_service.inference(sample_talent_profile)

        # Assert
        mock_company_search_adapter.search.assert_called_once()
        mock_news_search_adapter.search.assert_called_once()
        mock_llm_client.answer.assert_called_once()
        assert result == {
            "experience_tags": ["Software Development"],
            "skill_tags": ["Python"],
        }

    @pytest.mark.asyncio
    async def test_inference_no_company_context(
        self,
        talent_inference_service,
        mock_company_search_adapter,
        mock_news_search_adapter,
        mock_llm_client,
        sample_talent_profile,
    ):
        # Arrange
        mock_company_search_adapter.search.return_value = []
        mock_llm_client.answer.return_value = r"""```json
{"experience_tags": [], "skill_tags": []}
```"""

        # Act
        result = await talent_inference_service.inference(sample_talent_profile)

        # Assert
        mock_company_search_adapter.search.assert_called_once()
        mock_news_search_adapter.search.assert_not_called()
        mock_llm_client.answer.assert_called_once()
        assert result == {"experience_tags": [], "skill_tags": []}

    @pytest.mark.asyncio
    async def test_inference_llm_json_parse_error(
        self,
        talent_inference_service,
        mock_company_search_adapter,
        mock_news_search_adapter,
        mock_llm_client,
        sample_talent_profile,
        sample_company_context_a,
        sample_company_context_b,
        sample_news_chunk_a,
        sample_news_chunk_b,
    ):
        # Arrange
        mock_company_search_adapter.search.return_value = [
            sample_company_context_a,
            sample_company_context_b,
        ]
        mock_news_search_adapter.search.return_value = [
            NewsChunkByCompany(
                company_id=sample_company_context_a.company.id,
                news_chunks=[sample_news_chunk_a],
            ),
            NewsChunkByCompany(
                company_id=sample_company_context_b.company.id,
                news_chunks=[sample_news_chunk_b],
            ),
        ]
        mock_llm_client.answer.return_value = "Invalid JSON response"

        # Act
        result = await talent_inference_service.inference(sample_talent_profile)

        # Assert
        assert (
            "LLM 응답에서 JSON 형식이 올바르지 않습니다." in result["inference_result"]
        )
        assert "JSON 파싱에 실패했습니다." in result["error"]

    @pytest.mark.asyncio
    async def test_inference_llm_general_error(
        self,
        talent_inference_service,
        mock_company_search_adapter,
        mock_news_search_adapter,
        mock_llm_client,
        sample_talent_profile,
        sample_company_context_a,
        sample_company_context_b,
        sample_news_chunk_a,
        sample_news_chunk_b,
    ):
        # Arrange
        mock_company_search_adapter.search.return_value = [
            sample_company_context_a,
            sample_company_context_b,
        ]
        mock_news_search_adapter.search.return_value = [
            NewsChunkByCompany(
                company_id=sample_company_context_a.company.id,
                news_chunks=[sample_news_chunk_a],
            ),
            NewsChunkByCompany(
                company_id=sample_company_context_b.company.id,
                news_chunks=[sample_news_chunk_b],
            ),
        ]
        mock_llm_client.answer.side_effect = Exception("LLM API error")

        # Act
        result = await talent_inference_service.inference(sample_talent_profile)

        # Assert
        assert result == {
            "inference_result": "추론을 실패했습니다.",
            "error": "LLM API error",
        }

    def test_extract_company_params(
        self, talent_inference_service, sample_talent_profile
    ):
        # Act
        params = talent_inference_service._extract_company_params(sample_talent_profile)

        # Assert
        assert len(params) == 2
        assert params[0].alias == "Company A"
        assert params[0].start_date == date(2020, 1, 1)
        assert params[0].end_date == date(2021, 1, 31)  # Last day of month
        assert params[1].alias == "Company B"
        assert params[1].start_date == date(2021, 2, 1)
        assert params[1].end_date is None  # End date is None

    @pytest.mark.asyncio
    async def test_search_related_news(
        self,
        talent_inference_service,
        mock_news_search_adapter,
        sample_talent_profile,
        sample_company_context_a,
        sample_company_context_b,
        sample_news_chunk_a,
        sample_news_chunk_b,
    ):
        # Arrange
        company_contexts = [sample_company_context_a, sample_company_context_b]
        mock_news_search_adapter.search.return_value = [
            NewsChunkByCompany(
                company_id=sample_company_context_a.company.id,
                news_chunks=[sample_news_chunk_a],
            ),
            NewsChunkByCompany(
                company_id=sample_company_context_b.company.id,
                news_chunks=[sample_news_chunk_b],
            ),
        ]

        # Act
        news_by_companies = await talent_inference_service._search_related_news(
            sample_talent_profile, company_contexts
        )

        # Assert
        mock_news_search_adapter.search.assert_called_once()
        assert len(news_by_companies) == 2
        assert news_by_companies[sample_company_context_a.company.id] == [
            sample_news_chunk_a
        ]
        assert news_by_companies[sample_company_context_b.company.id] == [
            sample_news_chunk_b
        ]

    @pytest.mark.asyncio
    async def test_search_related_news_no_description(
        self,
        talent_inference_service,
        mock_news_search_adapter,
        sample_talent_profile,
        sample_company_context_a,
    ):
        # Arrange
        modified_positions = list(sample_talent_profile.positions)
        modified_positions[0] = Position(
            companyName=modified_positions[0].companyName,
            title=modified_positions[0].title,
            companyLocation=modified_positions[0].companyLocation,
            companyLogo=modified_positions[0].companyLogo,
            description="",
            startEndDate=modified_positions[0].startEndDate,
        )
        modified_talent_profile = TalentProfile(
            firstName=sample_talent_profile.firstName,
            lastName=sample_talent_profile.lastName,
            headline=sample_talent_profile.headline,
            summary=sample_talent_profile.summary,
            photoUrl=sample_talent_profile.photoUrl,
            linkedinUrl=sample_talent_profile.linkedinUrl,
            industryName=sample_talent_profile.industryName,
            positions=modified_positions,
        )
        company_contexts = [sample_company_context_a]

        # Act
        news_by_companies = await talent_inference_service._search_related_news(
            modified_talent_profile, company_contexts
        )

        # Assert
        mock_news_search_adapter.search.assert_not_called()
        assert news_by_companies == {}

    @pytest.mark.asyncio
    async def test_search_related_news_no_company_context_match(
        self,
        talent_inference_service,
        mock_news_search_adapter,
        sample_talent_profile,
        sample_company_context_a,
    ):
        # Arrange
        modified_positions = list(sample_talent_profile.positions)
        modified_positions[0] = Position(
            companyName="NonExistent Company",
            title=modified_positions[0].title,
            companyLocation=modified_positions[0].companyLocation,
            companyLogo=modified_positions[0].companyLogo,
            description=modified_positions[0].description,
            startEndDate=modified_positions[0].startEndDate,
        )
        modified_talent_profile = TalentProfile(
            firstName=sample_talent_profile.firstName,
            lastName=sample_talent_profile.lastName,
            headline=sample_talent_profile.headline,
            summary=sample_talent_profile.summary,
            photoUrl=sample_talent_profile.photoUrl,
            linkedinUrl=sample_talent_profile.linkedinUrl,
            industryName=sample_talent_profile.industryName,
            positions=modified_positions,
        )
        company_contexts = [sample_company_context_a]

        # Act
        news_by_companies = await talent_inference_service._search_related_news(
            modified_talent_profile, company_contexts
        )

        # Assert
        mock_news_search_adapter.search.assert_not_called()
        assert news_by_companies == {}

    @patch(
        "inference.application.services.talent_infer.TalentInferencePromptTemplates.get_talent_experience_inference_template"
    )
    def test_create_structured_prompt(
        self,
        mock_get_template,
        talent_inference_service,
        sample_talent_profile,
        sample_company_context_a,
        sample_news_chunk_a,
    ):
        # Arrange
        mock_template = MagicMock()
        mock_template.format.return_value = "Formatted Prompt"
        mock_get_template.return_value = mock_template

        career_journey = TalentCareerJourney(
            talent_profile=sample_talent_profile,
            position_contexts=[
                PositionWithContext(
                    position=sample_talent_profile.positions[0],
                    company_context=sample_company_context_a,
                    related_news=[sample_news_chunk_a],
                )
            ],
        )

        # Act
        prompt = talent_inference_service._create_structured_prompt(career_journey)

        # Assert
        mock_get_template.assert_called_once()
        mock_template.format.assert_called_once_with(
            talent_profile=sample_talent_profile,
            career_journey=career_journey,
            chronological_contexts=career_journey.get_chronological_journey(),
        )
        assert prompt == "Formatted Prompt"

    @pytest.mark.asyncio
    async def test_execute_llm_inference_success(
        self, talent_inference_service, mock_llm_client
    ):
        # Arrange
        formatted_prompt = "Some prompt text."
        mock_llm_client.answer.return_value = r"""```json
{"key": "value"}
```"""

        # Act
        result = await talent_inference_service._execute_llm_inference(formatted_prompt)

        # Assert
        mock_llm_client.answer.assert_called_once_with(
            question="", context=formatted_prompt, model=LLMModel.GPT_4O_MINI
        )
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_execute_llm_inference_invalid_json(
        self, talent_inference_service, mock_llm_client
    ):
        # Arrange
        formatted_prompt = "Some prompt text."
        mock_llm_client.answer.return_value = "Invalid JSON response"

        # Act
        result = await talent_inference_service._execute_llm_inference(formatted_prompt)

        # Assert
        assert (
            "LLM 응답에서 JSON 형식이 올바르지 않습니다." in result["inference_result"]
        )
        assert "JSON 파싱에 실패했습니다." in result["error"]

    @pytest.mark.asyncio
    async def test_execute_llm_inference_llm_client_error(
        self, talent_inference_service, mock_llm_client
    ):
        # Arrange
        formatted_prompt = "Some prompt text."
        mock_llm_client.answer.side_effect = Exception("LLM client error")

        # Act
        result = await talent_inference_service._execute_llm_inference(formatted_prompt)

        # Assert
        assert result == {
            "inference_result": "추론을 실패했습니다.",
            "error": "LLM client error",
        }

    def test_extract_date_range_with_end_date(self, talent_inference_service):
        # Arrange
        start_end_date = StartEndDate(
            start=DateModel(year=2020, month=1), end=DateModel(year=2021, month=12)
        )

        # Act
        start_date, end_date = talent_inference_service._extract_date_range(
            start_end_date
        )

        # Assert
        assert start_date == date(2020, 1, 1)
        assert end_date == date(2021, 12, 31)

    def test_extract_date_range_without_end_date(self, talent_inference_service):
        # Arrange
        start_end_date = StartEndDate(start=DateModel(year=2020, month=1), end=None)

        # Act
        start_date, end_date = talent_inference_service._extract_date_range(
            start_end_date
        )

        # Assert
        assert start_date == date(2020, 1, 1)
        assert end_date is None

    def test_extract_date_range_with_none_month(self, talent_inference_service):
        # Arrange
        start_end_date = StartEndDate(
            start=DateModel(year=2020, month=None), end=DateModel(year=2021, month=None)
        )

        # Act
        start_date, end_date = talent_inference_service._extract_date_range(
            start_end_date
        )

        # Assert
        assert start_date == date(2020, 1, 1)
        assert end_date is None
