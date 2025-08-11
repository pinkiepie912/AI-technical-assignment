from datetime import date
from typing import List
from uuid import uuid4

import pytest

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.vos.metrics import MonthlyMetrics


@pytest.fixture
def sample_company_id():
    """Generate a sample company ID for testing"""
    return uuid4()


@pytest.fixture
def sample_company(sample_company_id) -> Company:
    """Create a sample company entity for testing"""
    return Company(
        id=sample_company_id,
        external_id="TEST001",
        name="테스트 회사",
        name_en="Test Company",
        industry=["IT", "소프트웨어"],
        tags=["tech", "스타트업"],
        founded_date=date(2020, 1, 1),
        employee_count=50,
        stage="Series A",
        business_description="테스트용 회사입니다",
        ipo_date=None,
        total_investment=1000000000,
        origin_file_path="/test/path/file.json",
    )


@pytest.fixture
def sample_company_aliases(sample_company_id) -> List[CompanyAlias]:
    """Create sample company aliases for testing"""
    return [
        CompanyAlias(
            company_id=sample_company_id, alias="테스트 회사", alias_type="name", id=1
        ),
        CompanyAlias(
            company_id=sample_company_id, alias="Test Company", alias_type="name", id=2
        ),
    ]


@pytest.fixture
def sample_metrics_snapshots(sample_company_id) -> List[CompanyMetricsSnapshot]:
    """Create sample metrics snapshots for testing"""
    return [
        CompanyMetricsSnapshot(
            company_id=sample_company_id,
            reference_date=date(2024, 1, 1),
            metrics=MonthlyMetrics(
                mau=[], patents=[], finance=[], investments=[], organizations=[]
            ),
            id=1,
        )
    ]


@pytest.fixture
def sample_company_aggregate(
    sample_company: Company,
    sample_company_aliases: List[CompanyAlias],
    sample_metrics_snapshots: List[CompanyMetricsSnapshot],
) -> CompanyAggregate:
    """Create a sample CompanyAggregate for testing"""
    return CompanyAggregate(
        company=sample_company,
        company_aliases=sample_company_aliases,
        company_metrics_snapshots=sample_metrics_snapshots,
    )


@pytest.fixture
def minimal_company(sample_company_id) -> Company:
    """Create a minimal company entity for testing edge cases"""
    return Company(
        id=sample_company_id,
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


@pytest.fixture
def minimal_company_aggregate(minimal_company: Company) -> CompanyAggregate:
    """Create a minimal CompanyAggregate for testing edge cases"""
    return CompanyAggregate(
        company=minimal_company, company_aliases=[], company_metrics_snapshots=[]
    )

