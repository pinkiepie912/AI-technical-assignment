import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from enrichment.infrastructure.readers.exceptions import (
    ReaderEncodingError,
    ReaderFileNotFoundError,
    ReaderInvalidFormatError,
    ReaderValidationError,
)
from enrichment.infrastructure.readers.forest_of_hyuksin_reader import (
    ForestOfHyuksinReader,
)


class TestForestOfHyuksinReader:
    @pytest.fixture
    def reader(self) -> ForestOfHyuksinReader:
        return ForestOfHyuksinReader()

    def test_successful_file_reading_complete_data(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test successful reading of complete Forest of Hyuksin JSON data"""
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert
            assert result is not None
            assert len(result.mau.list) == 2
            assert result.mau.list[0].productId == "test_product_main"
            assert result.mau.list[1].productId == "test_product_secondary"
            assert result.dataSufficient is True
            assert (
                result.base_company_info.data.seedCorp.corpNameKr
                == "테스트코프 주식회사"
            )
            assert result.patent is not None
            assert result.patent.totalCount == 26
            assert result.customerType is not None
            assert len(result.customerType.salesFamily) == 3
            assert result.investment is not None
            assert result.investment.totalInvestmentAmount == 5000000000
        finally:
            test_file.unlink()

    def test_successful_file_reading_minimal_data(
        self,
        reader: ForestOfHyuksinReader,
        minimal_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test successful reading of minimal Forest of Hyuksin JSON data"""
        # Arrange
        test_file = temp_json_file(minimal_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert
            assert result is not None
            assert len(result.mau.list) == 0
            assert result.dataSufficient is False
            assert (
                result.base_company_info.data.seedCorp.corpNameKr == "미니멀 코퍼레이션"
            )
            assert result.patent is None  # Optional field
            assert result.customerType is None  # Optional field
            assert result.investment is None  # Optional field
        finally:
            test_file.unlink()

    def test_read_with_string_path(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(str(test_file))

            # Assert
            assert result is not None
            assert result.mau.list[0].productId == "test_product_main"
        finally:
            test_file.unlink()

    def test_file_not_found_error(self, reader: ForestOfHyuksinReader):
        # Arrange
        nonexistent_path = Path("/nonexistent/path/file.json")

        # Act & Assert
        with pytest.raises(ReaderFileNotFoundError) as exc_info:
            reader.read(nonexistent_path)

        assert str(nonexistent_path) in str(exc_info.value)
        assert exc_info.value.file_path == str(nonexistent_path)

    def test_directory_instead_of_file_error(self, reader: ForestOfHyuksinReader):
        # Arrange
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Act & Assert
            with pytest.raises(ReaderFileNotFoundError) as exc_info:
                reader.read(temp_dir)

            assert str(temp_dir) in str(exc_info.value)
        finally:
            temp_dir.rmdir()

    def test_invalid_json_format_error(
        self, reader: ForestOfHyuksinReader, invalid_json_file: Path
    ):
        try:
            # Act & Assert
            with pytest.raises(ReaderInvalidFormatError) as exc_info:
                reader.read(invalid_json_file)

            assert "JSON" in str(exc_info.value)
            assert str(invalid_json_file) in str(exc_info.value)
            assert exc_info.value.file_path == str(invalid_json_file)
        finally:
            invalid_json_file.unlink()

    def test_encoding_error(self, reader: ForestOfHyuksinReader, binary_file: Path):
        try:
            # Act & Assert
            with pytest.raises(ReaderEncodingError) as exc_info:
                reader.read(binary_file)

            assert "UTF-8" in str(exc_info.value)
            assert str(binary_file) in str(exc_info.value)
            assert exc_info.value.file_path == str(binary_file)
        finally:
            binary_file.unlink()

    def test_validation_error_invalid_schema(
        self,
        reader: ForestOfHyuksinReader,
        invalid_schema_data: Dict[str, Any],
        temp_json_file,
    ):
        # Arrange
        test_file = temp_json_file(invalid_schema_data)

        try:
            # Act & Assert
            with pytest.raises(ReaderValidationError) as exc_info:
                reader.read(test_file)

            assert "ForestOfHyuksin" in str(exc_info.value)
            assert str(test_file) in str(exc_info.value)
            assert exc_info.value.file_path == str(test_file)
        finally:
            test_file.unlink()

    def test_pydantic_validation_error_handling(
        self,
        reader: ForestOfHyuksinReader,
        incomplete_data: Dict[str, Any],
        temp_json_file,
    ):
        # Arrange
        test_file = temp_json_file(incomplete_data)

        try:
            # Act & Assert
            with pytest.raises(ReaderValidationError) as exc_info:
                reader.read(test_file)

            assert "ForestOfHyuksin" in str(exc_info.value)
            assert str(test_file) in str(exc_info.value)
        finally:
            test_file.unlink()

    @patch("pathlib.Path.open")
    def test_unexpected_file_read_error(
        self, mock_open: Mock, reader: ForestOfHyuksinReader
    ):
        # Arrange
        mock_open.side_effect = PermissionError("Access denied")
        temp_path = Path("/test/file.json")

        # Mock file existence check to pass
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "is_file", return_value=True),
        ):
            # Act & Assert
            with pytest.raises(ReaderInvalidFormatError) as exc_info:
                reader.read(temp_path)

            assert "Unexpected error" in str(exc_info.value)
            assert str(temp_path) in str(exc_info.value)

    def test_optional_fields_handling(
        self,
        reader: ForestOfHyuksinReader,
        minimal_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        # Arrange
        test_file = temp_json_file(minimal_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert
            assert result is not None
            assert result.patent is None  # Optional field should be None
            assert result.customerType is None  # Optional field should be None
            assert result.customerSales is None  # Optional field should be None
            assert result.investment is None  # Optional field should be None
            assert result.base_company_info.data.seedCorp.cordLat is None
            assert result.base_company_info.data.seedCorp.cordLng is None
            assert result.base_company_info.data.seedCorp.emplWholeVal is None
        finally:
            test_file.unlink()

    def test_korean_text_handling(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Verify Korean text is properly preserved
            assert (
                result.base_company_info.data.seedCorp.corpNameKr
                == "테스트코프 주식회사"
            )
            assert (
                result.base_company_info.data.seedCorp.bizInfoKr
                == "AI 기반 데이터 솔루션"
            )
            assert result.patent.list[0].title == "혁신적인 데이터 처리 방법"
            assert result.customerType.salesFamily[0].type == "1인 가구"
            assert "AI 솔루션" in [
                kw.advertisementKeyword
                for kw in result.base_company_info.data.seedAdvertisementKeywords
            ]
        finally:
            test_file.unlink()

    def test_complex_nested_structures(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test reading complex nested data structures"""
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Verify complex nested structures
            assert len(result.products) == 2
            assert len(result.products[0].types) == 3
            assert (
                result.products[0].types[2].url is None
            )  # Test Optional field in nested structure
            assert result.products[0].types[2].type == "IOS"

            assert len(result.customerType.salesPerson) == 3
            assert result.customerType.salesPerson[0].gender == "여성"
            assert result.customerType.salesPerson[0].ageGroup == "20대"

            assert len(result.base_company_info.data.seedCorpBiz) == 2
            assert result.base_company_info.data.seedCorpBiz[0].bizNameKr == "인공지능"
        finally:
            test_file.unlink()

    def test_interface_compliance(self, reader: ForestOfHyuksinReader):
        """Test that ForestOfHyuksinReader properly implements the expected interface"""
        # Assert
        assert hasattr(reader, "read")
        assert hasattr(reader, "validate_file_exists")
        assert callable(reader.read)
        assert callable(reader.validate_file_exists)

    def test_data_type_validation(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test that data types are properly validated and converted"""
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Verify correct data types
            assert isinstance(result.mau.list[0].data[0].value, int)
            assert isinstance(result.mau.list[0].data[0].growthRate, float)
            assert isinstance(result.dataSufficient, bool)
            assert isinstance(result.base_company_info.data.seedCorp.city, int)
            assert isinstance(result.base_company_info.data.seedCorp.showFlag, bool)
            assert isinstance(result.patent.averageRank, float)
            assert isinstance(result.organization.retireRate, float)
        finally:
            test_file.unlink()

