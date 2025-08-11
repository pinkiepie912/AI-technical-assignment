from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from typing import List

import pytest

from db.db import ReadSessionManager, WriteSessionManager
from enrichment.application.dtos.company import GetCompaniesMetricsSnapshotsPram
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.vos.metrics import MonthlyMetrics
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import (
    CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm,
)
from enrichment.infrastructure.repositories.company_repository import CompanyRepository
from inference.application.dtos.infer import GetCompaniesParam


class TestCompanyRepository:
    @pytest.fixture
    def mock_write_session_manager(self) -> MagicMock:
        """Mock WriteSessionManager for testing"""
        session_manager = MagicMock(spec=WriteSessionManager)
        mock_session = MagicMock()
        
        # Mock the query execution chain
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none = MagicMock(return_value=None)
        
        mock_session.execute = AsyncMock(return_value=mock_execute_result)
        mock_session.add = MagicMock()
        
        session_manager.__aenter__ = AsyncMock(return_value=mock_session)
        session_manager.__aexit__ = AsyncMock(return_value=None)
        
        return session_manager

    @pytest.fixture 
    def mock_read_session_manager(self) -> MagicMock:
        """Mock ReadSessionManager for testing"""
        session_manager = MagicMock(spec=ReadSessionManager)
        mock_session = MagicMock()
        
        # Mock scalars().all() chain
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_execute_result = MagicMock()
        mock_execute_result.scalars = MagicMock(return_value=mock_scalars)
        
        mock_session.execute = AsyncMock(return_value=mock_execute_result)
        
        session_manager.__aenter__ = AsyncMock(return_value=mock_session)
        session_manager.__aexit__ = AsyncMock(return_value=None)
        
        return session_manager

    @pytest.fixture
    def repository(self, mock_write_session_manager: MagicMock, mock_read_session_manager: MagicMock) -> CompanyRepository:
        """Create CompanyRepository with mocked session managers"""
        return CompanyRepository(mock_write_session_manager, mock_read_session_manager)

    @pytest.mark.asyncio
    async def test_save_complete_aggregate(
        self,
        repository: CompanyRepository,
        mock_write_session_manager: MagicMock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test saving a complete CompanyAggregate"""
        # Act
        await repository.save(sample_company_aggregate)

        # Assert
        # Verify session manager was used
        mock_write_session_manager.__aenter__.assert_called_once()
        mock_write_session_manager.__aexit__.assert_called_once()
        
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()

        # Verify company ORM object was created and added
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        assert company_orm.id == sample_company_aggregate.company.id
        assert company_orm.name == sample_company_aggregate.company.name
        assert company_orm.name_en == sample_company_aggregate.company.name_en
        assert company_orm.biz_categories == ["IT", "소프트웨어"]
        assert (
            company_orm.total_investment
            == sample_company_aggregate.company.total_investment
        )
        assert company_orm.founded_date == sample_company_aggregate.company.founded_date
        assert company_orm.ipo_date == sample_company_aggregate.company.ipo_date
        assert (
            company_orm.origin_file_path
            == sample_company_aggregate.company.origin_file_path
        )

        # Verify aliases were added
        alias_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyAliasOrm)
        ]
        assert len(alias_add_calls) == len(sample_company_aggregate.company_aliases)

        for i, call in enumerate(alias_add_calls):
            alias_orm = call[0][0]
            expected_alias = sample_company_aggregate.company_aliases[i]
            assert alias_orm.company_id == expected_alias.company_id
            assert alias_orm.alias == expected_alias.alias
            assert alias_orm.alias_type == expected_alias.alias_type

        # Verify snapshots were added
        snapshot_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyMetricsSnapshotOrm)
        ]
        assert len(snapshot_add_calls) == len(
            sample_company_aggregate.company_metrics_snapshots
        )

        for i, call in enumerate(snapshot_add_calls):
            snapshot_orm = call[0][0]
            expected_snapshot = sample_company_aggregate.company_metrics_snapshots[i]
            assert snapshot_orm.company_id == expected_snapshot.company_id
            assert snapshot_orm.reference_date == expected_snapshot.reference_date
            # Note: metrics should be converted to dict via to_dict()
            assert hasattr(snapshot_orm, "metrics")

    @pytest.mark.asyncio
    async def test_save_minimal_aggregate(
        self, repository: CompanyRepository, mock_write_session_manager: MagicMock
    ):
        """Test saving an aggregate with minimal data"""
        # Arrange
        company_id = uuid4()
        minimal_company = Company(
            id=company_id,
            external_id="MIN001",
            name="미니멀 회사",
            name_en=None,
            industry=[],
            tags=[],
            founded_date=None,
            employee_count=None,
            stage=None,
            business_description=None,
            ipo_date=None,
            total_investment=None,
            origin_file_path="/minimal/path.json",
        )

        minimal_aggregate = CompanyAggregate(
            company=minimal_company, company_aliases=[], company_metrics_snapshots=[]
        )

        # Act
        await repository.save(minimal_aggregate)

        # Assert
        # Verify session manager was used
        mock_write_session_manager.__aenter__.assert_called_once()
        mock_write_session_manager.__aexit__.assert_called_once()
        
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()

        # Verify company was added with None/empty values
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        assert company_orm.id == minimal_company.id
        assert company_orm.name == "미니멀 회사"
        assert company_orm.name_en is None
        assert company_orm.biz_categories == []  # Empty list from None industry
        assert company_orm.total_investment is None
        assert company_orm.founded_date is None
        assert company_orm.ipo_date is None

        # Verify no aliases were added
        alias_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyAliasOrm)
        ]
        assert len(alias_add_calls) == 0

        # Verify no snapshots were added
        snapshot_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyMetricsSnapshotOrm)
        ]
        assert len(snapshot_add_calls) == 0

    @pytest.mark.asyncio
    async def test_save_industry_splitting(
        self, repository: CompanyRepository, mock_write_session_manager: MagicMock
    ):
        """Test that industry string is properly split into categories"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            external_id="MULTI001",
            name="다업종 회사",
            name_en="Multi Industry Co",
            industry=["IT", "소프트웨어", "인공지능", "빅데이터"],
            tags=["tech", "AI"],
            founded_date=date(2020, 1, 1),
            employee_count=100,
            stage="Series B",
            business_description="다양한 업종의 회사",
            ipo_date=None,
            total_investment=2000000000,
            origin_file_path="/multi/industry.json",
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        # Act
        await repository.save(aggregate)

        # Assert
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()
        
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        expected_categories = ["IT", "소프트웨어", "인공지능", "빅데이터"]
        assert company_orm.biz_categories == expected_categories

    @pytest.mark.asyncio
    async def test_save_handles_session_context(
        self,
        repository: CompanyRepository,
        mock_write_session_manager: MagicMock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test that save method properly handles async session context"""
        # Arrange
        mock_write_session_manager.__aenter__ = AsyncMock()
        mock_write_session_manager.__aexit__ = AsyncMock()
        mock_session = MagicMock()
        mock_write_session_manager.__aenter__.return_value = mock_session

        # Act
        await repository.save(sample_company_aggregate)

        # Assert
        mock_write_session_manager.__aenter__.assert_called_once()
        mock_write_session_manager.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_empty_industry_handling(
        self, repository: CompanyRepository, mock_write_session_manager: MagicMock
    ):
        """Test handling of empty/None industry field"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            external_id="EMPTY001",
            name="업종 없는 회사",
            name_en="No Industry Co",
            industry=[],  # Empty list
            tags=[],
            founded_date=date(2020, 1, 1),
            employee_count=10,
            stage="Seed",
            business_description="업종이 명확하지 않은 회사",
            ipo_date=None,
            total_investment=100000000,
            origin_file_path="/empty/industry.json",
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        # Act
        await repository.save(aggregate)

        # Assert
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()
        
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        # Empty string should result in empty list, not [""]
        assert company_orm.biz_categories == []

    @pytest.mark.asyncio
    async def test_save_with_tags(
        self, repository: CompanyRepository, mock_write_session_manager: MagicMock
    ):
        """Test saving a company with tags field"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            external_id="TAG001",
            name="태그가 있는 회사",
            name_en="Tagged Company",
            industry=["IT", "소프트웨어"],
            tags=["스타트업", "AI", "혁신기업", "빅데이터"],
            founded_date=date(2021, 5, 15),
            employee_count=200,
            stage="Series C",
            business_description="다양한 태그를 가진 기업",
            ipo_date=None,
            total_investment=5000000000,
            origin_file_path="/tags/company.json",
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        # Act
        await repository.save(aggregate)

        # Assert
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()
        
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        # Verify industry is correctly mapped to biz_categories
        assert company_orm.biz_categories == ["IT", "소프트웨어"]
        # Note: tags field would need to be handled by the ORM mapping
        # This test verifies the Company entity supports tags properly

    @pytest.mark.asyncio
    async def test_save_empty_tags_handling(
        self, repository: CompanyRepository, mock_write_session_manager: MagicMock
    ):
        """Test handling of empty tags field"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            external_id="NOTAG001",
            name="태그 없는 회사",
            name_en="No Tags Co",
            industry=["IT"],
            tags=[],  # Empty tags list
            founded_date=date(2020, 1, 1),
            employee_count=10,
            stage="Seed",
            business_description="태그가 없는 회사",
            ipo_date=None,
            total_investment=100000000,
            origin_file_path="/no/tags.json",
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        # Act
        await repository.save(aggregate)

        # Assert
        # Get the mock session to verify calls
        mock_session = await mock_write_session_manager.__aenter__()
        
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        assert company_orm.biz_categories == ["IT"]
        # Tags should be handled appropriately - empty list should be fine

    def test_constructor(self):
        """Test CompanyRepository constructor"""
        # Arrange
        mock_write_session_manager = MagicMock(spec=WriteSessionManager)
        mock_read_session_manager = MagicMock(spec=ReadSessionManager)

        # Act
        repository = CompanyRepository(mock_write_session_manager, mock_read_session_manager)

        # Assert
        assert repository.write_session_manager is mock_write_session_manager
        assert repository.read_session_manager is mock_read_session_manager
        assert isinstance(repository, CompanyRepository)

    # Tests for get_companies method
    @pytest.mark.asyncio
    async def test_get_companies_empty_params(
        self,
        repository: CompanyRepository,
        mock_read_session_manager: MagicMock,
    ):
        """Test get_companies with empty params list"""
        # Act
        result = await repository.get_companies([])

        # Assert
        assert result == []
        # Verify no database queries were made
        mock_read_session_manager.__aenter__.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_companies_no_matching_aliases(
        self,
        repository: CompanyRepository,
        mock_read_session_manager: MagicMock,
    ):
        """Test get_companies when no aliases match"""
        # Arrange
        params = [
            GetCompaniesParam(
                alias="nonexistent-company",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
        ]

        # Act
        result = await repository.get_companies(params)

        # Assert
        assert result == []
        # Verify session manager was used at least once
        assert mock_read_session_manager.__aenter__.call_count >= 1
        assert mock_read_session_manager.__aexit__.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_companies_with_matching_data(
        self,
        repository: CompanyRepository,
        mock_read_session_manager: MagicMock,
    ):
        """Test get_companies with matching data"""
        # Arrange
        company_id = uuid4()
        params = [
            GetCompaniesParam(
                alias="test-company",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
        ]

        # Mock alias ORM
        alias_orm = CompanyAliasOrm(
            id=1,
            company_id=company_id,
            alias="test-company",
            alias_type="name"
        )

        # Mock company ORM
        company_orm = CompanyOrm(
            id=company_id,
            external_id="TEST001",
            name="테스트 회사",
            name_en="Test Company",
            biz_categories=["IT", "소프트웨어"],
            biz_tags=["tech", "스타트업"],
            biz_description="테스트용 회사입니다",
            stage="Series A",
            total_investment=1000000000,
            founded_date=date(2020, 1, 1),
            ipo_date=None,
            employee_count=50,
            origin_file_path="/test/path/file.json"
        )

        # Mock metrics snapshot ORM
        snapshot_orm = CompanyMetricsSnapshotOrm(
            id=1,
            company_id=company_id,
            reference_date=date(2024, 1, 1),
            metrics={
                "mau": [],
                "patents": [],
                "finance": [],
                "investments": [],
                "organizations": []
            }
        )

        # Set up mock session to return proper responses
        def mock_execute_side_effect(query):
            mock_execute_result = MagicMock()
            mock_scalars = MagicMock()
            
            # Check query type based on the table being queried
            query_str = str(query)
            if "company_alias" in query_str.lower():
                # Return alias for alias query
                mock_scalars.all = MagicMock(return_value=[alias_orm])
            elif "company_metrics_snapshot" in query_str.lower():
                # Return snapshot for metrics query
                mock_scalars.all = MagicMock(return_value=[snapshot_orm])
            else:
                # Return company for company query
                mock_scalars.all = MagicMock(return_value=[company_orm])
            
            mock_execute_result.scalars = MagicMock(return_value=mock_scalars)
            return mock_execute_result
        
        # Modify the existing mock session setup
        mock_read_session_manager._session_instance = MagicMock()
        mock_read_session_manager._session_instance.execute = AsyncMock(side_effect=mock_execute_side_effect)
        mock_read_session_manager.__aenter__ = AsyncMock(return_value=mock_read_session_manager._session_instance)

        # Act
        result = await repository.get_companies(params)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], CompanyAggregate)
        assert result[0].company.id == company_id
        assert result[0].company.name == "테스트 회사"
        assert len(result[0].company_aliases) == 1
        assert result[0].company_aliases[0].alias == "test-company"
        assert len(result[0].company_metrics_snapshots) == 1
        
        # Verify session manager was used
        assert mock_read_session_manager.__aenter__.call_count >= 1
        assert mock_read_session_manager.__aexit__.call_count >= 1

    @pytest.mark.asyncio 
    async def test_get_companies_multiple_params(
        self,
        repository: CompanyRepository,
        mock_read_session_manager: MagicMock,
    ):
        """Test get_companies with multiple company params"""
        # Arrange
        company_id1 = uuid4()
        company_id2 = uuid4()
        
        params = [
            GetCompaniesParam(
                alias="company-1",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 6, 30)
            ),
            GetCompaniesParam(
                alias="company-2", 
                start_date=date(2024, 7, 1),
                end_date=date(2024, 12, 31)
            )
        ]

        # Mock alias ORMs
        alias_orm1 = CompanyAliasOrm(id=1, company_id=company_id1, alias="company-1", alias_type="name")
        alias_orm2 = CompanyAliasOrm(id=2, company_id=company_id2, alias="company-2", alias_type="name")

        # Mock company ORMs
        company_orm1 = CompanyOrm(
            id=company_id1, external_id="COMP001", name="회사1", name_en="Company 1",
            biz_categories=["IT"], biz_tags=["tech"], biz_description="첫번째 회사",
            stage="Series A", total_investment=500000000, founded_date=date(2019, 1, 1),
            ipo_date=None, employee_count=25, origin_file_path="/test/comp1.json"
        )
        company_orm2 = CompanyOrm(
            id=company_id2, external_id="COMP002", name="회사2", name_en="Company 2",
            biz_categories=["Finance"], biz_tags=["fintech"], biz_description="두번째 회사",
            stage="Series B", total_investment=1000000000, founded_date=date(2020, 1, 1),
            ipo_date=None, employee_count=75, origin_file_path="/test/comp2.json"
        )

        # Set up mock session
        def mock_execute_side_effect(query):
            mock_execute_result = MagicMock()
            mock_scalars = MagicMock()
            
            query_str = str(query)
            if "company_alias" in query_str.lower():
                # Return both aliases for alias query
                mock_scalars.all = MagicMock(return_value=[alias_orm1, alias_orm2])
            elif "company_metrics_snapshot" in query_str.lower():
                # Return empty snapshots for metrics query
                mock_scalars.all = MagicMock(return_value=[])
            else:
                # Return both companies for company query
                mock_scalars.all = MagicMock(return_value=[company_orm1, company_orm2])
            
            mock_execute_result.scalars = MagicMock(return_value=mock_scalars)
            return mock_execute_result
        
        # Modify the existing mock session setup
        mock_read_session_manager._session_instance = MagicMock()
        mock_read_session_manager._session_instance.execute = AsyncMock(side_effect=mock_execute_side_effect)
        mock_read_session_manager.__aenter__ = AsyncMock(return_value=mock_read_session_manager._session_instance)

        # Act
        result = await repository.get_companies(params)

        # Assert
        assert len(result) == 2
        
        # Find results by company name
        comp1_result = next((r for r in result if r.company.name == "회사1"), None)
        comp2_result = next((r for r in result if r.company.name == "회사2"), None)
        
        assert comp1_result is not None
        assert comp2_result is not None
        assert comp1_result.company.external_id == "COMP001"
        assert comp2_result.company.external_id == "COMP002"
        
        # Verify session manager was used
        assert mock_read_session_manager.__aenter__.call_count >= 1
        assert mock_read_session_manager.__aexit__.call_count >= 1

