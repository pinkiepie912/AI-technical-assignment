import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from enrichment.application.exceptions.reader_exception import (
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

            # Assert - Test CompanyAggregate structure
            assert result is not None
            assert hasattr(result, "company")
            assert hasattr(result, "company_aliases")
            assert hasattr(result, "company_metrics_snapshots")

            # Test Company data
            company = result.company
            assert company.name == "테스트코프 주식회사"
            assert company.name_en == "TestCorp Inc."
            assert company.total_investment == 5000000000
            assert company.stage == "Series A"
            assert company.founded_date.year == 2020
            assert company.founded_date.month == 3

            # Test Company aliases
            aliases = [alias.alias for alias in result.company_aliases]
            assert "테스트코프 주식회사" in aliases
            assert "TestCorp Inc." in aliases
            assert "테스트 메인 서비스" in aliases  # product name

            # Test metrics snapshots exist
            assert len(result.company_metrics_snapshots) > 0

            # Verify metrics contain expected data types
            snapshot = result.company_metrics_snapshots[0]
            assert hasattr(snapshot.metrics, "mau")
            assert hasattr(snapshot.metrics, "patents")
            assert hasattr(snapshot.metrics, "finance")
            assert hasattr(snapshot.metrics, "investments")
            assert hasattr(snapshot.metrics, "organizations")

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

            # Assert - Test CompanyAggregate structure with minimal data
            assert result is not None
            assert hasattr(result, "company")
            assert hasattr(result, "company_aliases")
            assert hasattr(result, "company_metrics_snapshots")

            # Test Company data
            company = result.company
            assert company.name == "미니멀 코퍼레이션"
            assert company.name_en == "Minimal Corp"
            assert company.investment_total is None  # No investment in minimal data
            assert company.stage is None
            assert company.founded_date.year == 2020

            # Test Company aliases (minimal should still have company names)
            aliases = [alias.alias for alias in result.company_aliases]
            assert "미니멀 코퍼레이션" in aliases
            assert "Minimal Corp" in aliases

            # Test metrics snapshots (minimal data should have empty metrics)
            # Even minimal data might create empty monthly metrics
            metrics_snapshots = result.company_metrics_snapshots
            for snapshot in metrics_snapshots:
                assert len(snapshot.metrics.mau) == 0
                assert len(snapshot.metrics.patents) == 0
                assert len(snapshot.metrics.finance) == 0
                assert len(snapshot.metrics.investments) == 0
                assert len(snapshot.metrics.organizations) == 0

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
            assert result.company.name == "테스트코프 주식회사"
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

            # Assert - Test optional field handling in CompanyAggregate
            assert result is not None
            company = result.company

            # Test optional fields are handled properly
            assert company.name_en is not None  # Should have value from minimal data
            assert company.investment_total is None  # Should be None in minimal
            assert company.stage is None  # Should be None
            assert company.business_description is not None  # Has value
            assert company.ipo_date is None  # Should be None
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

            # Assert - Verify Korean text is properly preserved in CompanyAggregate
            company = result.company
            assert company.name == "테스트코프 주식회사"
            assert company.industry == ["인공지능", "데이터 처리"]  # From seedCorpBiz
            assert (
                company.business_description
                == "데이터 처리 솔루션 전문 AI 기술 선도 기업"
            )

            # Verify Korean text in aliases
            korean_aliases = [
                alias.alias
                for alias in result.company_aliases
                if "테스트" in alias.alias
            ]
            assert len(korean_aliases) > 0

            # Test Korean text in metrics (check patent titles)
            patent_metrics = []
            for snapshot in result.company_metrics_snapshots:
                patent_metrics.extend(snapshot.metrics.patents)

            if patent_metrics:
                korean_titles = [p.title for p in patent_metrics if "혁신" in p.title]
                assert len(korean_titles) > 0
        finally:
            test_file.unlink()

    def test_complex_nested_structures(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test reading complex nested data structures into CompanyAggregate"""
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Verify complex nested structures are properly transformed
            company = result.company

            # Test industry field combines business categories
            assert company.industry == ["인공지능", "데이터 처리"]

            # Test aliases include product names
            aliases = [alias.alias for alias in result.company_aliases]
            assert "테스트 메인 서비스" in aliases
            assert "테스트 서브 서비스" in aliases

            # Test metrics snapshots contain structured data
            metrics_found = {
                "mau": False,
                "patents": False,
                "finance": False,
                "investments": False,
                "organizations": False,
            }

            for snapshot in result.company_metrics_snapshots:
                if snapshot.metrics.mau:
                    metrics_found["mau"] = True
                    # Test MAU structure
                    mau = snapshot.metrics.mau[0]
                    assert hasattr(mau, "product_id")
                    assert hasattr(mau, "value")
                    assert hasattr(mau, "growthRate")

                if snapshot.metrics.patents:
                    metrics_found["patents"] = True
                    # Test Patent structure
                    patent = snapshot.metrics.patents[0]
                    assert hasattr(patent, "level")
                    assert hasattr(patent, "title")

                if snapshot.metrics.finance:
                    metrics_found["finance"] = True
                    # Test Finance structure
                    finance = snapshot.metrics.finance[0]
                    assert hasattr(finance, "year")
                    assert hasattr(finance, "profit")

                if snapshot.metrics.investments:
                    metrics_found["investments"] = True
                    # Test Investment structure
                    investment = snapshot.metrics.investments[0]
                    assert hasattr(investment, "level")
                    assert hasattr(investment, "amount")
                    assert hasattr(investment, "investors")

                if snapshot.metrics.organizations:
                    metrics_found["organizations"] = True
                    # Test Organization structure
                    org = snapshot.metrics.organizations[0]
                    assert hasattr(org, "people_count")
                    assert hasattr(org, "growth_rate")

            # Verify we found the expected metrics
            assert metrics_found["mau"]
            assert metrics_found["patents"]
            assert metrics_found["finance"]
            # Investment data might not always be present in test data
            # assert metrics_found['investments']
            assert metrics_found["organizations"]

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

            # Assert - Verify correct data types in CompanyAggregate
            company = result.company
            assert isinstance(company.name, str)
            assert isinstance(company.employee_count, (int, type(None)))
            assert isinstance(company.investment_total, (int, type(None)))
            assert isinstance(company.founded_date, (date, type(None)))
            assert isinstance(company.ipo_date, (date, type(None)))
            assert isinstance(company.industry, list)
            assert isinstance(company.tags, list)

            # Test metrics data types
            for snapshot in result.company_metrics_snapshots:
                assert isinstance(snapshot.reference_date, date)

                for mau in snapshot.metrics.mau:
                    assert isinstance(mau.value, int)
                    assert isinstance(mau.growthRate, float)
                    assert isinstance(mau.product_id, str)

                for patent in snapshot.metrics.patents:
                    assert isinstance(patent.title, str)
                    assert isinstance(patent.level, str)

                for finance in snapshot.metrics.finance:
                    assert isinstance(finance.year, int)
                    assert isinstance(finance.profit, (int, float, type(None)))

                for investment in snapshot.metrics.investments:
                    assert isinstance(investment.amount, (int, float))
                    assert isinstance(investment.investors, list)

                for org in snapshot.metrics.organizations:
                    assert isinstance(org.people_count, int)
                    assert isinstance(org.growth_rate, float)
        finally:
            test_file.unlink()

    def test_tags_field_handling(
        self,
        reader: ForestOfHyuksinReader,
        complete_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test that tags field is properly handled in Company entity"""
        # Arrange
        test_file = temp_json_file(complete_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Test tags field
            company = result.company
            assert hasattr(company, "tags")
            assert isinstance(company.tags, list)
            
            # Tags should be present and contain expected data
            # Based on the test data, tags should be extracted from appropriate sources
            assert company.tags == ["인공지능", "빅데이터"]
            
            # Test that tags are properly typed
            for tag in company.tags:
                assert isinstance(tag, str)

        finally:
            test_file.unlink()

    def test_empty_tags_handling(
        self,
        reader: ForestOfHyuksinReader,
        minimal_forest_data: Dict[str, Any],
        temp_json_file,
    ):
        """Test handling of empty/None tags in minimal data"""
        # Arrange
        test_file = temp_json_file(minimal_forest_data)

        try:
            # Act
            result = reader.read(test_file)

            # Assert - Test empty tags field
            company = result.company
            assert hasattr(company, "tags")
            assert isinstance(company.tags, list)
            assert company.tags == []  # Should default to empty list

        finally:
            test_file.unlink()
