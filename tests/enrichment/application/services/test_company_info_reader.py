from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from enrichment.application.services.company_info_reader import CompanyInfoReader
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.specs.company_spec import CompanySearchParam


@pytest.fixture
def mock_company_repository():
    return AsyncMock()


@pytest.fixture
def mock_embedding_client():
    return MagicMock()


@pytest.fixture
def company_info_reader(mock_company_repository, mock_embedding_client):
    return CompanyInfoReader(
        repository=mock_company_repository, embedding_client=mock_embedding_client
    )


@pytest.mark.asyncio
async def test_get_companies_success(company_info_reader, mock_company_repository):
    # Arrange
    search_params = [
        CompanySearchParam(
            alias="Test Company 1",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
        ),
        CompanySearchParam(
            alias="Test Company 2",
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31),
        ),
    ]

    mock_company_1 = CompanyAggregate(
        company=Company(
            id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
            external_id="EXT1",
            name="Test Company 1",
            name_en="Test Company 1 EN",
            business_description="Desc 1",
            employee_count=100,
            founded_date=date(2019, 1, 1),
            ipo_date=None,
            industry=[],
            tags=[],
            stage=None,
            total_investment=None,
            origin_file_path="/path/to/file1.json",
        ),
        company_aliases=[],
        company_metrics_snapshots=[],
    )
    mock_company_2 = CompanyAggregate(
        company=Company(
            id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"),
            external_id="EXT2",
            name="Test Company 2",
            name_en="Test Company 2 EN",
            business_description="Desc 2",
            employee_count=200,
            founded_date=date(2020, 1, 1),
            ipo_date=None,
            industry=[],
            tags=[],
            stage=None,
            total_investment=None,
            origin_file_path="/path/to/file2.json",
        ),
        company_aliases=[],
        company_metrics_snapshots=[],
    )

    mock_company_repository.get_companies.return_value = [
        mock_company_1,
        mock_company_2,
    ]

    # Act
    result = await company_info_reader.get_companies(search_params)

    # Assert
    mock_company_repository.get_companies.assert_called_once()
    assert len(result) == 2
    assert result[0].company.name == "Test Company 1"
    assert result[1].company.name == "Test Company 2"


@pytest.mark.asyncio
async def test_get_companies_empty_params(company_info_reader, mock_company_repository):
    # Arrange
    search_params = []
    mock_company_repository.get_companies.return_value = []

    # Act
    result = await company_info_reader.get_companies(search_params)

    # Assert
    mock_company_repository.get_companies.assert_called_once_with([])
    assert len(result) == 0
