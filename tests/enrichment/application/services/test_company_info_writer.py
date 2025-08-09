from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from enrichment.application.dtos.file_process import FileProcessResult
from enrichment.application.services.company_info_writer import CompanyInfoWriter
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.infrastructure.readers.exceptions import (
    ReaderEncodingError,
    ReaderFileNotFoundError,
    ReaderInvalidFormatError,
    ReaderValidationError,
)
from enrichment.infrastructure.readers.interfaces import JSONDataReader
from enrichment.infrastructure.repositories.company_repository import CompanyRepository


class TestCompanyInfoWriter:
    @pytest.fixture
    def mock_reader(self) -> Mock:
        """Mock JSONDataReader for testing"""
        return Mock(spec=JSONDataReader)

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """Mock CompanyRepository for testing"""
        mock_repo = Mock(spec=CompanyRepository)
        mock_repo.save = AsyncMock()
        return mock_repo

    @pytest.fixture
    def service(self, mock_reader: Mock, mock_repository: Mock) -> CompanyInfoWriter:
        """Create CompanyInfoWriter with mocked dependencies"""
        return CompanyInfoWriter(mock_reader, mock_repository)

    # Using shared fixtures from tests/conftest.py:
    # - sample_company_aggregate

    @pytest.mark.asyncio
    async def test_process_file_success(
        self,
        service: CompanyInfoWriter,
        mock_reader: Mock,
        mock_repository: Mock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test successful file processing"""
        # Arrange
        file_path = "/test/valid_file.json"
        mock_reader.read.return_value = sample_company_aggregate

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

            # Assert
            assert isinstance(result, FileProcessResult)
            assert result.success is True
            assert result.company_id == sample_company_aggregate.company.id
            assert result.message is None

            # Verify dependencies were called correctly
            mock_reader.read.assert_called_once_with(file_path)
            mock_repository.save.assert_called_once_with(sample_company_aggregate)

    @pytest.mark.asyncio
    async def test_process_file_not_found(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of non-existent file"""
        # Arrange
        file_path = "/nonexistent/file.json"

        # Act
        result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert "File not found" in result.message
        assert file_path in result.message

        # Verify reader and repository were not called
        mock_reader.read.assert_not_called()
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_file_reader_file_not_found_error(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of ReaderFileNotFoundError from reader"""
        # Arrange
        file_path = "/test/missing_file.json"
        mock_reader.read.side_effect = ReaderFileNotFoundError(file_path)

        # Mock Path.exists to return True to pass the initial check
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

            # Assert
            assert isinstance(result, FileProcessResult)
            assert result.success is False
            assert result.company_id is None
            assert "File not found" in result.message

            # Verify reader was called but repository was not
            mock_reader.read.assert_called_once_with(file_path)
            mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_file_reader_invalid_format_error(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of ReaderInvalidFormatError from reader"""
        # Arrange
        file_path = "/test/invalid_format.json"
        error_message = "Invalid JSON format"
        mock_reader.read.side_effect = ReaderInvalidFormatError(
            file_path, "JSON", error_message
        )

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert error_message in result.message

        # Verify reader was called but repository was not
        mock_reader.read.assert_called_once_with(file_path)
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_file_reader_encoding_error(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of ReaderEncodingError from reader"""
        # Arrange
        file_path = "/test/encoding_issue.json"
        error_message = "Invalid encoding"
        mock_reader.read.side_effect = ReaderEncodingError(
            file_path, "UTF-8", error_message
        )

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert error_message in result.message

        # Verify reader was called but repository was not
        mock_reader.read.assert_called_once_with(file_path)
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_file_reader_validation_error(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of ReaderValidationError from reader"""
        # Arrange
        file_path = "/test/validation_error.json"
        error_message = "Schema validation failed"
        mock_reader.read.side_effect = ReaderValidationError(
            file_path, "ForestOfHyuksin", error_message
        )

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert error_message in result.message

        # Verify reader was called but repository was not
        mock_reader.read.assert_called_once_with(file_path)
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_file_repository_save_error(
        self,
        service: CompanyInfoWriter,
        mock_reader: Mock,
        mock_repository: Mock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test handling of repository save error"""
        # Arrange
        file_path = "/test/save_error.json"
        error_message = "Database connection failed"
        mock_reader.read.return_value = sample_company_aggregate
        mock_repository.save.side_effect = Exception(error_message)

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert error_message in result.message

        # Verify both reader and repository were called
        mock_reader.read.assert_called_once_with(file_path)
        mock_repository.save.assert_called_once_with(sample_company_aggregate)

    @pytest.mark.asyncio
    async def test_process_file_with_string_path(
        self,
        service: CompanyInfoWriter,
        mock_reader: Mock,
        mock_repository: Mock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test processing file with string path (not Path object)"""
        # Arrange
        file_path = "/test/string_path.json"
        mock_reader.read.return_value = sample_company_aggregate

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is True
        assert result.company_id == sample_company_aggregate.company.id

        # Verify reader received string path
        mock_reader.read.assert_called_once_with(file_path)

    @pytest.mark.asyncio
    async def test_process_file_generic_exception(
        self, service: CompanyInfoWriter, mock_reader: Mock, mock_repository: Mock
    ):
        """Test handling of generic exceptions"""
        # Arrange
        file_path = "/test/generic_error.json"
        error_message = "Unexpected error occurred"
        mock_reader.read.side_effect = RuntimeError(error_message)

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert isinstance(result, FileProcessResult)
        assert result.success is False
        assert result.company_id is None
        assert error_message in result.message

        # Verify reader was called but repository was not
        mock_reader.read.assert_called_once_with(file_path)
        mock_repository.save.assert_not_called()

    def test_constructor(self):
        """Test CompanyInfoWriter constructor"""
        # Arrange
        mock_reader = Mock(spec=JSONDataReader)
        mock_repository = Mock(spec=CompanyRepository)

        # Act
        service = CompanyInfoWriter(mock_reader, mock_repository)

        # Assert
        assert service.reader is mock_reader
        assert service.repository is mock_repository
        assert isinstance(service, CompanyInfoWriter)

    @pytest.mark.asyncio
    async def test_file_process_result_structure(
        self,
        service: CompanyInfoWriter,
        mock_reader: Mock,
        mock_repository: Mock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test that FileProcessResult has the correct structure"""
        # Arrange
        file_path = "/test/result_structure.json"
        mock_reader.read.return_value = sample_company_aggregate

        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = await service.process_file(file_path)

        # Assert
        assert hasattr(result, "success")
        assert hasattr(result, "company_id")
        assert hasattr(result, "message")
        assert isinstance(result.success, bool)
        assert result.company_id is not None  # Should have UUID
        assert result.message is None  # Should be None for success case

