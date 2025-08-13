"""Test cases for Forest of Hyuksin reader"""
import json
import pytest
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from enrichment.infrastructure.readers.forest_of_hyuksin_reader import ForestOfHyuksinReader
from enrichment.domain.exceptions.company_reader_exceptions import (
    ReaderFileNotFoundError,
    ReaderInvalidFormatError,
    ReaderEncodingError,
    ReaderValidationError
)


class TestForestOfHyuksinReader:
    @pytest.fixture
    def reader(self):
        return ForestOfHyuksinReader()
    
    @pytest.fixture
    def sample_data(self):
        """Sample valid Forest of Hyuksin data structure"""
        return {
            "base_company_info": {
                "data": {
                    "seedCorp": {
                        "id": "test-corp-id",
                        "corpNameKr": "테스트회사",
                        "corpNameEn": "Test Corp",
                        "corpIntroKr": "테스트용 회사입니다",
                        "emplWholeVal": 100,
                        "foundAt": "2020-01-15",
                        "listingDate": "2023-06-30",
                    },
                    "seedCorpBiz": [
                        {"bizNameKr": "IT", "bizNameEn": "Information Technology"},
                        {"bizNameKr": "소프트웨어", "bizNameEn": "Software"}
                    ],
                    "seedCorpTag": [
                        {"tagNameKr": "스타트업", "tagNameEn": "Startup"},
                        {"tagNameKr": "AI", "tagNameEn": "AI"}
                    ]
                }
            },
            "products": [
                {"id": "prod1", "name": "제품A"},
                {"id": "prod2", "name": "제품B"}
            ],
            "investment": {
                "data": [
                    {
                        "level": "Seed",
                        "investAt": "2023-03-15",
                        "investmentAmount": 1000000000,
                        "investor": [
                            {"name": "벤처캐피탈A"},
                            {"name": "투자자B"}
                        ]
                    }
                ],
                "totalInvestmentAmount": 1000000000,
                "lastInvestmentLevel": "Seed"
            },
            "mau": {
                "list": [
                    {
                        "productId": "prod1",
                        "data": [
                            {
                                "value": 50000,
                                "growthRate": 15.5,
                                "referenceMonth": "2023-12"
                            }
                        ]
                    }
                ]
            },
            "patent": {
                "list": [
                    {
                        "level": "국내특허",
                        "title": "AI 알고리즘 특허",
                        "registerAt": "2023-06-15"
                    }
                ]
            },
            "finance": {
                "data": [
                    {
                        "year": 2023,
                        "profit": 1000000000,
                        "operatingProfit": 800000000,
                        "netProfit": 600000000
                    }
                ]
            },
            "organization": {
                "data": [
                    {
                        "value": 120,
                        "growRate": 20.0,
                        "referenceMonth": "2023-12"
                    }
                ]
            }
        }
    
    def test_read_file_not_found(self, reader):
        with pytest.raises(ReaderFileNotFoundError):
            reader.read("non_existent_file.json")
    
    def test_read_invalid_json(self, reader):
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("invalid json {")
            temp_file_path = temp_file.name
        
        try:
            with pytest.raises(ReaderInvalidFormatError) as exc_info:
                reader.read(temp_file_path)
            
            assert "JSON" in str(exc_info.value)
        finally:
            Path(temp_file_path).unlink()
    
    def test_read_encoding_error(self, reader):
        # Create file with invalid UTF-8 encoding
        with NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as temp_file:
            temp_file.write(b'\xff\xfe{"invalid": "encoding"}')  # Invalid UTF-8
            temp_file_path = temp_file.name
        
        try:
            with pytest.raises(ReaderEncodingError) as exc_info:
                reader.read(temp_file_path)
            
            assert "UTF-8" in str(exc_info.value)
        finally:
            Path(temp_file_path).unlink()
    
    def test_read_validation_error(self, reader):
        # Create JSON with invalid structure
        invalid_data = {"invalid": "structure"}
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(invalid_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            with pytest.raises(ReaderValidationError) as exc_info:
                reader.read(temp_file_path)
            
            assert "ForestOfHyuksin" in str(exc_info.value)
        finally:
            Path(temp_file_path).unlink()
    
    def test_read_success_minimal(self, reader, minimal_forest_of_hyuksin_data):
        # Use the minimal valid data from conftest
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(minimal_forest_of_hyuksin_data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            # Test basic company info from minimal conftest fixture
            assert aggregate.company.external_id == "CP00001521"
            assert aggregate.company.name == "테스트회사"
            assert aggregate.company.name_en == "Test Corp"
            assert aggregate.company.business_description == "테스트 회사 설명"
            assert aggregate.company.employee_count == 25
            assert aggregate.company.founded_date == date(2016, 7, 7)
            assert len(aggregate.company_aliases) >= 2  # Company names + product names
            assert len(aggregate.company_metrics_snapshots) == 0  # No metrics in minimal data
        finally:
            Path(temp_file_path).unlink()
    
    def test_read_success_comprehensive(self, reader, complete_forest_of_hyuksin_data):
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(complete_forest_of_hyuksin_data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            # Test company data from complete conftest fixture (밀리의서재 data)
            company = aggregate.company
            assert company.external_id == "CP00001521"
            assert company.name == "밀리의서재"
            assert company.name_en == "MILLY'S LIBRARY CO.,LTD."
            assert company.business_description == "전자책 정기구독 플랫폼 '밀리의 서재'를 운영하는 기업"
            assert company.employee_count == 73
            assert company.founded_date == date(2016, 7, 7)
            assert company.ipo_date == date(2023, 9, 27)
            assert company.industry == ["콘텐츠/예술"]
            assert company.tags == ["웹툰/만화", "OTT", "구독"]
            assert company.stage == "IPO"
            assert company.total_investment == 62650000000
            assert company.origin_file_path == str(Path(temp_file_path).absolute())
            
            # Test aliases (company names + product names)
            aliases = aggregate.company_aliases
            alias_names = {alias.alias for alias in aliases}
            assert "밀리의서재" in alias_names
            assert "MILLY'S LIBRARY CO.,LTD." in alias_names
            assert len(aliases) >= 2
            
            # Test metrics snapshots
            snapshots = aggregate.company_metrics_snapshots
            assert len(snapshots) > 0
            
            # Check that we have snapshots for different dates
            snapshot_dates = {snapshot.reference_date for snapshot in snapshots}
            assert date(2022, 3, 1) in snapshot_dates   # MAU data
            assert date(2018, 11, 1) in snapshot_dates  # Patent data
            assert date(2023, 9, 1) in snapshot_dates   # Investment data
            assert date(2025, 1, 1) in snapshot_dates   # Organization data
            
            # Test specific MAU metrics in snapshots
            mau_snapshot = next((s for s in snapshots if s.reference_date == date(2022, 3, 1) and s.metrics.mau), None)
            if mau_snapshot:
                assert len(mau_snapshot.metrics.mau) == 1
                assert mau_snapshot.metrics.mau[0].product_name == "밀리의서재"
                assert mau_snapshot.metrics.mau[0].value == 726765
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_create_company_aliases_deduplication(self, reader, minimal_forest_of_hyuksin_data):
        # Add duplicate names to test deduplication
        test_data = minimal_forest_of_hyuksin_data.copy()
        test_data["products"] = [
            {"id": "prod1", "name": "테스트회사", "types": [], "finishedAt": None, "logoImgUrl": ""},  # Same as company name
            {"id": "prod2", "name": "Test Corp", "types": [], "finishedAt": None, "logoImgUrl": ""}   # Same as English company name
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            # Should not have duplicates - only unique names
            alias_names = {alias.alias for alias in aggregate.company_aliases}
            assert len(alias_names) == 2  # Only unique names
            assert "테스트회사" in alias_names
            assert "Test Corp" in alias_names
        finally:
            Path(temp_file_path).unlink()
    
    def test_metrics_collection_with_invalid_dates(self, reader, complete_forest_of_hyuksin_data):
        # Use complete data and add invalid dates to test filtering
        data_with_invalid_dates = complete_forest_of_hyuksin_data.copy()
        
        # Add invalid date entries alongside valid ones
        data_with_invalid_dates["mau"]["list"][0]["data"].append({
            "value": 1000,
            "growthRate": 10.0,
            "referenceMonth": "invalid-date"
        })
        
        data_with_invalid_dates["patent"]["list"].append({
            "level": "국내특허",
            "title": "특허1",
            "registerAt": "invalid-date"
        })
        
        data_with_invalid_dates["organization"]["data"].append({
            "value": 100,
            "growRate": 15.0,
            "referenceMonth": "invalid-date",
            "in": 0,
            "out": 0
        })
        
        data_with_invalid_dates["investment"]["data"].append({
            "level": "Seed",
            "investAt": "invalid-date",
            "investmentAmount": 1000000
        })
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data_with_invalid_dates, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            # Should only include metrics with valid dates
            snapshots = aggregate.company_metrics_snapshots
            
            # Check that valid data from conftest is still processed
            valid_dates = {snapshot.reference_date for snapshot in snapshots}
            assert date(2022, 3, 1) in valid_dates   # MAU data from conftest
            assert date(2018, 11, 1) in valid_dates  # Patent data from conftest
            
            # Check that only valid MAU data is included
            mau_snapshot = next((s for s in snapshots if s.reference_date == date(2022, 3, 1) and s.metrics.mau), None)
            if mau_snapshot:
                # Should include original valid data, invalid data should be filtered out
                assert len(mau_snapshot.metrics.mau) == 1
                assert mau_snapshot.metrics.mau[0].value == 726765  # Original valid value from conftest
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_investment_data_validation(self, reader, minimal_forest_of_hyuksin_data):
        # Modify minimal data to include invalid investment entries
        data_with_invalid_investment = minimal_forest_of_hyuksin_data.copy()
        data_with_invalid_investment["investment"]["data"] = [
            {"level": "Seed", "investmentAmount": 1000000},  # No investAt
            {"level": "Series A", "investAt": None, "investmentAmount": 2000000},  # investAt is None
            {"level": "Series B", "investAt": "2023-06-15", "investmentAmount": 3000000, "investor": [{"name": "VC"}]}  # Valid
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data_with_invalid_investment, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            # Should only include valid investment data
            investment_snapshots = [s for s in aggregate.company_metrics_snapshots if s.metrics.investments]
            assert len(investment_snapshots) == 1
            
            investment_snapshot = investment_snapshots[0]
            assert len(investment_snapshot.metrics.investments) == 1
            assert investment_snapshot.metrics.investments[0].level == "Series B"
            assert investment_snapshot.metrics.investments[0].amount == 3000000
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_investor_names_extraction(self, reader, minimal_forest_of_hyuksin_data):
        # Modify minimal data to include invalid investor structures
        data = minimal_forest_of_hyuksin_data.copy()
        data["investment"]["data"] = [
            {
                "level": "Seed",
                "investAt": "2023-03-15",
                "investmentAmount": 1000000,
                "investor": [
                    {"name": "유효한 투자자"},
                    {"invalid": "structure"},  # No name field
                    {"name": None},  # Name is None
                    {"name": "또다른 투자자"},
                    "invalid_format"  # Not a dict
                ]
            }
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            investment_snapshot = next(s for s in aggregate.company_metrics_snapshots if s.metrics.investments)
            investment = investment_snapshot.metrics.investments[0]
            
            # Should only include valid investor names
            assert set(investment.investors) == {"유효한 투자자", "또다른 투자자"}
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_path_handling(self, reader, minimal_forest_of_hyuksin_data):
        # Test with both string and Path objects
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(minimal_forest_of_hyuksin_data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            # Test with string path
            aggregate1 = reader.read(temp_file_path)
            
            # Test with Path object
            aggregate2 = reader.read(Path(temp_file_path))
            
            # Both should produce identical results
            assert aggregate1.company.external_id == aggregate2.company.external_id
            assert aggregate1.company.origin_file_path == aggregate2.company.origin_file_path
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_optional_fields_handling(self, reader, minimal_forest_of_hyuksin_data):
        """Test handling of optional fields that may be None or missing"""
        # Modify the minimal data to have None values for optional fields
        data_with_none_fields = minimal_forest_of_hyuksin_data.copy()
        data_with_none_fields["base_company_info"]["data"]["seedCorp"].update({
            "corpNameEn": "",  # Optional field as None
            "corpIntroKr": "",
            "emplWholeVal": None,
            "foundAt": "",
            "listingDate": None
        })
        data_with_none_fields["investment"] = None  # Optional field as None
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data_with_none_fields, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            aggregate = reader.read(temp_file_path)
            
            company = aggregate.company
            assert company.external_id == "CP00001521"  # From conftest data
            assert company.name == "테스트회사"  # From conftest data
            assert company.name_en is None
            assert company.business_description is None
            assert company.employee_count == 0  # None becomes 0
            assert company.founded_date is None
            assert company.ipo_date is None
            assert company.total_investment is None
            assert company.stage is None
            
        finally:
            Path(temp_file_path).unlink()