"""Test cases for Company repository"""
import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4
from collections import defaultdict

from enrichment.infrastructure.repositories.company_repository import CompanyRepository, GetCompaniesMetricsSnapshotsPram
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.specs.company_spec import CompanySearchParam
from enrichment.domain.vos.metrics import MonthlyMetrics
from enrichment.infrastructure.exceptions.repository_exception import DuplicatedCompanyError
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm


class TestCompanyRepository:
    @pytest.fixture
    def mock_write_session_manager(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_read_session_manager(self):
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_write_session_manager, mock_read_session_manager):
        return CompanyRepository(
            write_session_manager=mock_write_session_manager,
            read_session_manager=mock_read_session_manager
        )
    
    @pytest.fixture
    def sample_company_aggregate(self):
        company_id = UUID("12345678-1234-5678-9abc-123456789012")
        
        company = Company(
            id=company_id,
            external_id="test-external-id",
            name="테스트회사",
            name_en="Test Company",
            industry=["IT", "Software"],
            tags=["startup", "ai"],
            founded_date=date(2020, 1, 15),
            employee_count=100,
            stage="Series A",
            business_description="AI 기반 서비스 회사",
            ipo_date=date(2023, 6, 30),
            total_investment=5000000000,
            origin_file_path="/data/company.json"
        )
        
        aliases = [
            CompanyAlias(
                company_id=company_id,
                alias="테스트회사",
                alias_type="company_name",
                id=1
            ),
            CompanyAlias(
                company_id=company_id,
                alias="Test Company",
                alias_type="company_name",
                id=2
            )
        ]
        
        metrics = MonthlyMetrics(
            mau=[], patents=[], finance=[], investments=[], organizations=[]
        )
        snapshots = [
            CompanyMetricsSnapshot(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics=metrics,
                id=1
            )
        ]
        
        return CompanyAggregate(
            company=company,
            company_aliases=aliases,
            company_metrics_snapshots=snapshots
        )

    @pytest.mark.asyncio
    async def test_save_success(self, repository, sample_company_aggregate, mock_write_session_manager):
        # Mock session and execute method
        mock_session = AsyncMock()
        mock_write_session_manager.__aenter__.return_value = mock_session
        
        # Mock that company doesn't exist (no duplicate)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        await repository.save(sample_company_aggregate)
        
        # Verify session.add was called for company, aliases, and snapshots
        assert mock_session.add.call_count == 4  # 1 company + 2 aliases + 1 snapshot
    
    @pytest.mark.asyncio
    async def test_save_duplicate_company_error(self, repository, sample_company_aggregate, mock_write_session_manager):
        # Mock session and execute method
        mock_session = AsyncMock()
        mock_write_session_manager.__aenter__.return_value = mock_session
        
        # Mock that company already exists
        existing_company = CompanyOrm(id=uuid4(), external_id="test-external-id", name="Existing Company")
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_company
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(DuplicatedCompanyError):
            await repository.save(sample_company_aggregate)
    
    @pytest.mark.asyncio
    async def test_get_companies_empty_params(self, repository):
        result = await repository.get_companies([])
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_companies_success(self, repository, mock_read_session_manager):
        # Mock session
        mock_session = AsyncMock()
        mock_read_session_manager.__aenter__.return_value = mock_session
        
        company_id = UUID("12345678-1234-5678-9abc-123456789012")
        
        # Mock alias lookup
        alias_orm = CompanyAliasOrm(
            company_id=company_id,
            alias="테스트회사",
            alias_type="company_name",
            id=1
        )
        mock_aliases_result = Mock()
        mock_aliases_result.scalars().all.return_value = [alias_orm]
        
        # Mock company lookup
        company_orm = CompanyOrm(
            id=company_id,
            external_id="test-external-id",
            name="테스트회사",
            name_en="Test Company",
            biz_categories=["IT"],
            biz_tags=["startup"],
            founded_date=date(2020, 1, 15),
            employee_count=100,
            stage="Series A",
            biz_description="AI 회사",
            ipo_date=date(2023, 6, 30),
            total_investment=5000000000,
            origin_file_path="/data/company.json"
        )
        mock_company_result = Mock()
        mock_company_result.scalars().all.return_value = [company_orm]
        
        # Mock metrics snapshot lookup
        snapshot_orm = CompanyMetricsSnapshotOrm(
            company_id=company_id,
            reference_date=date(2023, 12, 31),
            metrics={"mau": [], "patents": [], "finance": [], "investments": [], "organizations": []},
            id=1
        )
        mock_snapshot_result = Mock()
        mock_snapshot_result.scalars().all.return_value = [snapshot_orm]
        
        # Configure session.execute to return appropriate results
        mock_session.execute.side_effect = [
            mock_aliases_result,
            mock_company_result,
            mock_snapshot_result
        ]
        
        # Execute test
        params = [
            CompanySearchParam(
                alias="테스트회사",
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31)
            )
        ]
        
        result = await repository.get_companies(params)
        
        assert len(result) == 1
        aggregate = result[0]
        assert aggregate.company.id == company_id
        assert aggregate.company.name == "테스트회사"
        assert len(aggregate.company_aliases) == 1
        assert len(aggregate.company_metrics_snapshots) == 1
    
    @pytest.mark.asyncio
    async def test_get_companies_no_matching_aliases(self, repository, mock_read_session_manager):
        # Mock session
        mock_session = AsyncMock()
        mock_read_session_manager.__aenter__.return_value = mock_session
        
        # Mock alias lookup with no results
        mock_aliases_result = Mock()
        mock_aliases_result.scalars().all.return_value = []
        mock_session.execute.return_value = mock_aliases_result
        
        params = [
            CompanySearchParam(
                alias="존재하지않는회사",
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31)
            )
        ]
        
        result = await repository.get_companies(params)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_aliases_map_by_empty_list(self, repository):
        mock_session = AsyncMock()
        result = await repository._get_aliases_map_by([], mock_session)
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_aliases_map_by_success(self, repository):
        mock_session = AsyncMock()
        
        alias_orm1 = CompanyAliasOrm(alias="테스트회사", company_id=uuid4(), alias_type="company_name", id=1)
        alias_orm2 = CompanyAliasOrm(alias="Test Company", company_id=uuid4(), alias_type="company_name", id=2)
        
        mock_result = Mock()
        mock_result.scalars().all.return_value = [alias_orm1, alias_orm2]
        mock_session.execute.return_value = mock_result
        
        result = await repository._get_aliases_map_by(["테스트회사", "Test Company"], mock_session)
        
        assert len(result) == 2
        assert result["테스트회사"] == alias_orm1
        assert result["Test Company"] == alias_orm2
    
    @pytest.mark.asyncio
    async def test_get_companies_empty_list(self, repository):
        mock_session = AsyncMock()
        result = await repository._get_companies([], mock_session)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_companies_success_single(self, repository):
        mock_session = AsyncMock()
        company_id = uuid4()
        
        company_orm = CompanyOrm(id=company_id, external_id="test", name="Test Company")
        mock_result = Mock()
        mock_result.scalars().all.return_value = [company_orm]
        mock_session.execute.return_value = mock_result
        
        result = await repository._get_companies([company_id], mock_session)
        
        assert len(result) == 1
        assert result[0] == company_orm
    
    @pytest.mark.asyncio
    async def test_get_companies_metrics_snapshots_empty_params(self, repository):
        mock_session = AsyncMock()
        result = await repository._get_companies_metrics_snapshots([], mock_session)
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_companies_metrics_snapshots_success(self, repository):
        mock_session = AsyncMock()
        company_id = uuid4()
        
        snapshot_orm = CompanyMetricsSnapshotOrm(
            company_id=company_id,
            reference_date=date(2023, 12, 31),
            metrics={},
            id=1
        )
        mock_result = Mock()
        mock_result.scalars().all.return_value = [snapshot_orm]
        mock_session.execute.return_value = mock_result
        
        params = [
            GetCompaniesMetricsSnapshotsPram(
                company_id=company_id,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31)
            )
        ]
        
        result = await repository._get_companies_metrics_snapshots(params, mock_session)
        
        assert len(result) == 1
        assert company_id in result
        assert len(result[company_id]) == 1
        assert result[company_id][0] == snapshot_orm
    
    @pytest.mark.asyncio
    async def test_get_companies_metrics_snapshots_with_default_end_date(self, repository):
        mock_session = AsyncMock()
        company_id = uuid4()
        
        snapshot_orm = CompanyMetricsSnapshotOrm(
            company_id=company_id,
            reference_date=date(2023, 12, 31),
            metrics={},
            id=1
        )
        mock_result = Mock()
        mock_result.scalars().all.return_value = [snapshot_orm]
        mock_session.execute.return_value = mock_result
        
        # Test with end_date=None (should use today's date)
        params = [
            GetCompaniesMetricsSnapshotsPram(
                company_id=company_id,
                start_date=date(2023, 1, 1),
                end_date=None
            )
        ]
        
        result = await repository._get_companies_metrics_snapshots(params, mock_session)
        
        assert len(result) == 1
        assert company_id in result
    
    def test_create_company_aggregate(self, repository):
        company_id = uuid4()
        
        company_orm = CompanyOrm(
            id=company_id,
            external_id="test-id",
            name="테스트회사",
            name_en="Test Company",
            biz_categories=["IT"],
            biz_tags=["startup"],
            founded_date=date(2020, 1, 15),
            employee_count=100,
            stage="Series A",
            biz_description="AI 회사",
            ipo_date=date(2023, 6, 30),
            total_investment=5000000000,
            origin_file_path="/data/company.json"
        )
        
        alias_orms = [
            CompanyAliasOrm(
                company_id=company_id,
                alias="테스트회사",
                alias_type="company_name",
                id=1
            )
        ]
        
        snapshot_orms = [
            CompanyMetricsSnapshotOrm(
                company_id=company_id,
                reference_date=date(2023, 12, 31),
                metrics={"mau": [], "patents": [], "finance": [], "investments": [], "organizations": []},
                id=1
            )
        ]
        
        aggregate = repository._create_company_aggregate(
            company_orm=company_orm,
            alias_orms=alias_orms,
            snapshot_orm=snapshot_orms
        )
        
        assert isinstance(aggregate, CompanyAggregate)
        assert aggregate.company.id == company_id
        assert aggregate.company.name == "테스트회사"
        assert len(aggregate.company_aliases) == 1
        assert len(aggregate.company_metrics_snapshots) == 1
    
    def test_create_company_from_orm(self, repository):
        company_id = uuid4()
        orm = CompanyOrm(
            id=company_id,
            external_id="test-id",
            name="테스트회사",
            name_en="Test Company",
            biz_categories=["IT", "Software"],
            biz_tags=["startup", "ai"],
            founded_date=date(2020, 1, 15),
            employee_count=100,
            stage="Series A",
            biz_description="AI 기반 서비스 회사",
            ipo_date=date(2023, 6, 30),
            total_investment=5000000000,
            origin_file_path="/data/company.json"
        )
        
        company = repository._create_company_from(orm)
        
        assert company.id == company_id
        assert company.external_id == "test-id"
        assert company.name == "테스트회사"
        assert company.name_en == "Test Company"
        assert company.industry == ["IT", "Software"]
        assert company.tags == ["startup", "ai"]
        assert company.founded_date == date(2020, 1, 15)
        assert company.employee_count == 100
        assert company.stage == "Series A"
        assert company.business_description == "AI 기반 서비스 회사"
        assert company.ipo_date == date(2023, 6, 30)
        assert company.total_investment == 5000000000
        assert company.origin_file_path == "/data/company.json"
    
    def test_create_company_from_orm_with_none_values(self, repository):
        company_id = uuid4()
        orm = CompanyOrm(
            id=company_id,
            external_id="test-id",
            name="테스트회사",
            name_en=None,
            biz_categories=None,
            biz_tags=None,
            founded_date=None,
            employee_count=100,
            stage=None,
            biz_description=None,
            ipo_date=None,
            total_investment=None,
            origin_file_path=None
        )
        
        company = repository._create_company_from(orm)
        
        assert company.name_en == ""
        assert company.industry == []
        assert company.tags == []
        assert company.founded_date is None
        assert company.stage == ""
        assert company.business_description == ""
        assert company.ipo_date is None
        assert company.total_investment is None
        assert company.origin_file_path == ""
    
    def test_create_alias_from_orm(self, repository):
        company_id = uuid4()
        alias_orm = CompanyAliasOrm(
            company_id=company_id,
            alias="테스트회사",
            alias_type="company_name",
            id=1
        )
        
        alias = repository._create_alias_from(alias_orm)
        
        assert alias.company_id == company_id
        assert alias.alias == "테스트회사"
        assert alias.alias_type == "company_name"
        assert alias.id == 1
    
    def test_create_snapshots_from_orm(self, repository):
        company_id = uuid4()
        snapshot_orm = CompanyMetricsSnapshotOrm(
            company_id=company_id,
            reference_date=date(2023, 12, 31),
            metrics={
                "mau": [],
                "patents": [],
                "finance": [],
                "investments": [],
                "organizations": []
            },
            id=1
        )
        
        snapshot = repository._create_snapshots_from(snapshot_orm)
        
        assert snapshot.company_id == company_id
        assert snapshot.reference_date == date(2023, 12, 31)
        assert isinstance(snapshot.metrics, MonthlyMetrics)
        assert snapshot.id == 1
    
    @pytest.mark.asyncio
    async def test_get_companies_multiple_params_and_results(self, repository, mock_read_session_manager):
        """Test with multiple search parameters and results"""
        mock_session = AsyncMock()
        mock_read_session_manager.__aenter__.return_value = mock_session
        
        company_id1 = UUID("12345678-1234-5678-9abc-123456789012")
        company_id2 = UUID("87654321-4321-8765-cba9-876543210987")
        
        # Mock alias lookup - return multiple aliases
        alias_orm1 = CompanyAliasOrm(company_id=company_id1, alias="회사A", alias_type="company_name", id=1)
        alias_orm2 = CompanyAliasOrm(company_id=company_id2, alias="회사B", alias_type="company_name", id=2)
        mock_aliases_result = Mock()
        mock_aliases_result.scalars().all.return_value = [alias_orm1, alias_orm2]
        
        # Mock company lookup - return multiple companies
        company_orm1 = CompanyOrm(id=company_id1, external_id="ext1", name="회사A")
        company_orm2 = CompanyOrm(id=company_id2, external_id="ext2", name="회사B")
        mock_company_result = Mock()
        mock_company_result.scalars().all.return_value = [company_orm1, company_orm2]
        
        # Mock empty snapshots
        mock_snapshot_result = Mock()
        mock_snapshot_result.scalars().all.return_value = []
        
        mock_session.execute.side_effect = [
            mock_aliases_result,
            mock_company_result,
            mock_snapshot_result
        ]
        
        params = [
            CompanySearchParam(alias="회사A", start_date=date(2023, 1, 1)),
            CompanySearchParam(alias="회사B", start_date=date(2023, 1, 1))
        ]
        
        result = await repository.get_companies(params)
        
        assert len(result) == 2
        company_names = {agg.company.name for agg in result}
        assert company_names == {"회사A", "회사B"}