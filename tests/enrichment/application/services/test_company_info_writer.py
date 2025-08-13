from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from enrichment.application.services.company_info_writer import CompanyInfoWriter
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.exceptions.company_reader_exceptions import (
    ReaderInvalidFormatError,
)
from enrichment.infrastructure.exceptions.repository_exception import RepositoryError


@pytest.fixture
def mock_company_reader():
    return MagicMock()


@pytest.fixture
def mock_company_repository():
    return AsyncMock()


@pytest.fixture
def company_info_writer(mock_company_reader, mock_company_repository):
    return CompanyInfoWriter(
        reader=mock_company_reader, repository=mock_company_repository
    )


@pytest.mark.asyncio
async def test_process_file_not_found(company_info_writer):
    # Arrange
    non_existent_file = "/path/to/non_existent_file.json"

    # Act
    result = await company_info_writer.process_file(non_existent_file)

    # Assert
    assert not result.success
    assert "File not found" in result.message


@pytest.mark.asyncio
async def test_process_file_success(
    company_info_writer, mock_company_reader, mock_company_repository
):
    # Arrange
    file_content = "{}"
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    mock_company = Company(
        id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13"),
        external_id="EXT1",
        name="Test Company",
        name_en="Test Company EN",
        business_description="Desc",
        employee_count=100,
        founded_date=None,
        ipo_date=None,
        industry=[],
        tags=[],
        stage=None,
        total_investment=None,
        origin_file_path=temp_file_path,
    )
    mock_aggregate = CompanyAggregate(
        company=mock_company, company_aliases=[], company_metrics_snapshots=[]
    )
    mock_company_reader.read.return_value = mock_aggregate
    mock_company_repository.save.return_value = None

    # Act
    result = await company_info_writer.process_file(temp_file_path)

    # Assert
    assert result.success
    assert result.company_id == mock_company.id
    mock_company_reader.read.assert_called_once_with(temp_file_path)
    mock_company_repository.save.assert_called_once_with(mock_aggregate)

    # Cleanup
    Path(temp_file_path).unlink()


@pytest.mark.asyncio
async def test_process_file_reader_exception(company_info_writer, mock_company_reader):
    # Arrange
    file_content = "invalid json"
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    mock_company_reader.read.side_effect = ReaderInvalidFormatError(
        temp_file_path, "JSON", "Invalid format"
    )

    # Act
    result = await company_info_writer.process_file(temp_file_path)

    # Assert
    assert not result.success
    assert "Invalid format" in result.message
    mock_company_reader.read.assert_called_once_with(temp_file_path)

    # Cleanup
    Path(temp_file_path).unlink()


@pytest.mark.asyncio
async def test_process_file_repository_exception(
    company_info_writer, mock_company_reader, mock_company_repository
):
    # Arrange
    file_content = "{}"
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    mock_company = Company(
        id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13"),
        external_id="EXT1",
        name="Test Company",
        name_en="Test Company EN",
        business_description="Desc",
        employee_count=100,
        founded_date=None,
        ipo_date=None,
        industry=[],
        tags=[],
        stage=None,
        total_investment=None,
        origin_file_path=temp_file_path,
    )
    mock_aggregate = CompanyAggregate(
        company=mock_company, company_aliases=[], company_metrics_snapshots=[]
    )
    mock_company_reader.read.return_value = mock_aggregate
    mock_company_repository.save.side_effect = RepositoryError("Database error")

    # Act
    result = await company_info_writer.process_file(temp_file_path)

    # Assert
    assert not result.success
    assert isinstance(result.message, str) and "Database error" in result.message
    mock_company_reader.read.assert_called_once_with(temp_file_path)
    mock_company_repository.save.assert_called_once_with(mock_aggregate)

    # Cleanup
    Path(temp_file_path).unlink()
