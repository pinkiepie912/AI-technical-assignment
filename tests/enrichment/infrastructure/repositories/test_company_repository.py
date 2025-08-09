from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from db.db import WriteSessionManager
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import (
    CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm,
)
from enrichment.infrastructure.repositories.company_repository import CompanyRepository


class TestCompanyRepository:
    @pytest.fixture
    def mock_session_manager(self) -> MagicMock:
        """Mock WriteSessionManager for testing"""
        session_manager = MagicMock(spec=WriteSessionManager)
        mock_session = MagicMock()
        session_manager.__aenter__.return_value = mock_session
        session_manager.__aexit__.return_value = None
        return session_manager

    @pytest.fixture
    def repository(self, mock_session_manager: MagicMock) -> CompanyRepository:
        """Create CompanyRepository with mocked session manager"""
        return CompanyRepository(mock_session_manager)

    @pytest.mark.asyncio
    async def test_save_complete_aggregate(
        self,
        repository: CompanyRepository,
        mock_session_manager: MagicMock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test saving a complete CompanyAggregate"""
        # Arrange
        mock_session = mock_session_manager.__aenter__.return_value

        # Act
        await repository.save(sample_company_aggregate)

        # Assert
        # Verify session manager was used
        mock_session_manager.__aenter__.assert_called_once()
        mock_session_manager.__aexit__.assert_called_once()

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
        self, repository: CompanyRepository, mock_session_manager: MagicMock
    ):
        """Test saving an aggregate with minimal data"""
        # Arrange
        company_id = uuid4()
        minimal_company = Company(
            id=company_id,
            name="미니멀 회사",
            name_en=None,
            industry=None,
            founded_date=None,
            employee_count=None,
            investment_total=None,
            stage=None,
            business_description=None,
            ipo_date=None,
            total_investment=None,
            origin_file_path="/minimal/path.json",
            company_aliases=[],
            company_snapshot=[],
        )

        minimal_aggregate = CompanyAggregate(
            company=minimal_company, company_aliases=[], company_metrics_snapshots=[]
        )

        mock_session = mock_session_manager.__aenter__.return_value

        # Act
        await repository.save(minimal_aggregate)

        # Assert
        # Verify session manager was used
        mock_session_manager.__aenter__.assert_called_once()
        mock_session_manager.__aexit__.assert_called_once()

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
        self, repository: CompanyRepository, mock_session_manager: MagicMock
    ):
        """Test that industry string is properly split into categories"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            name="다업종 회사",
            name_en="Multi Industry Co",
            industry="IT, 소프트웨어, 인공지능, 빅데이터",
            founded_date=date(2020, 1, 1),
            employee_count=100,
            investment_total=2000000000,
            stage="Series B",
            business_description="다양한 업종의 회사",
            ipo_date=None,
            total_investment=2000000000,
            origin_file_path="/multi/industry.json",
            company_aliases=[],
            company_snapshot=[],
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        mock_session = mock_session_manager.__aenter__.return_value

        # Act
        await repository.save(aggregate)

        # Assert
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
        mock_session_manager: MagicMock,
        sample_company_aggregate: CompanyAggregate,
    ):
        """Test that save method properly handles async session context"""
        # Arrange
        mock_session_manager.__aenter__ = AsyncMock()
        mock_session_manager.__aexit__ = AsyncMock()
        mock_session = MagicMock()
        mock_session_manager.__aenter__.return_value = mock_session

        # Act
        await repository.save(sample_company_aggregate)

        # Assert
        mock_session_manager.__aenter__.assert_called_once()
        mock_session_manager.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_empty_industry_handling(
        self, repository: CompanyRepository, mock_session_manager: MagicMock
    ):
        """Test handling of empty/None industry field"""
        # Arrange
        company_id = uuid4()
        company = Company(
            id=company_id,
            name="업종 없는 회사",
            name_en="No Industry Co",
            industry="",  # Empty string
            founded_date=date(2020, 1, 1),
            employee_count=10,
            investment_total=100000000,
            stage="Seed",
            business_description="업종이 명확하지 않은 회사",
            ipo_date=None,
            total_investment=100000000,
            origin_file_path="/empty/industry.json",
            company_aliases=[],
            company_snapshot=[],
        )

        aggregate = CompanyAggregate(
            company=company, company_aliases=[], company_metrics_snapshots=[]
        )

        mock_session = mock_session_manager.__aenter__.return_value

        # Act
        await repository.save(aggregate)

        # Assert
        company_add_calls = [
            call
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], CompanyOrm)
        ]
        assert len(company_add_calls) == 1

        company_orm = company_add_calls[0][0][0]
        # Empty string should result in empty list, not [""]
        assert company_orm.biz_categories == []

    def test_constructor(self):
        """Test CompanyRepository constructor"""
        # Arrange
        mock_session_manager = MagicMock(spec=WriteSessionManager)

        # Act
        repository = CompanyRepository(mock_session_manager)

        # Assert
        assert repository.session_manager is mock_session_manager
        assert isinstance(repository, CompanyRepository)

