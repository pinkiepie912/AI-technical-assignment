"""Test fixtures for infrastructure tests"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date
from uuid import UUID, uuid4

from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.vos.metrics import MonthlyMetrics
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm


@pytest.fixture
def mock_async_session():
    """Mock async database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def mock_session_manager():
    """Mock session manager for database operations"""
    manager = AsyncMock()
    return manager


@pytest.fixture
def sample_company_id():
    """Sample company UUID"""
    return UUID("12345678-1234-5678-9abc-123456789012")


@pytest.fixture
def sample_company(sample_company_id):
    """Sample Company entity"""
    return Company(
        id=sample_company_id,
        external_id="sample-external-id",
        name="샘플회사",
        name_en="Sample Company",
        industry=["Technology", "Software"],
        tags=["startup", "ai", "saas"],
        founded_date=date(2020, 3, 15),
        employee_count=150,
        stage="Series B",
        business_description="AI 기반 SaaS 플랫폼을 제공하는 스타트업",
        ipo_date=date(2023, 9, 20),
        total_investment=10000000000,
        origin_file_path="/data/sample_company.json"
    )


@pytest.fixture
def sample_company_aliases(sample_company_id):
    """Sample CompanyAlias entities"""
    return [
        CompanyAlias(
            company_id=sample_company_id,
            alias="샘플회사",
            alias_type="company_name",
            id=1
        ),
        CompanyAlias(
            company_id=sample_company_id,
            alias="Sample Company",
            alias_type="company_name",
            id=2
        ),
        CompanyAlias(
            company_id=sample_company_id,
            alias="SampleApp",
            alias_type="product_name",
            id=3
        )
    ]


@pytest.fixture
def sample_monthly_metrics():
    """Sample MonthlyMetrics value object"""
    return MonthlyMetrics(
        mau=[],
        patents=[],
        finance=[],
        investments=[],
        organizations=[]
    )


@pytest.fixture
def sample_company_metrics_snapshots(sample_company_id, sample_monthly_metrics):
    """Sample CompanyMetricsSnapshot entities"""
    return [
        CompanyMetricsSnapshot(
            company_id=sample_company_id,
            reference_date=date(2023, 12, 31),
            metrics=sample_monthly_metrics,
            id=1
        ),
        CompanyMetricsSnapshot(
            company_id=sample_company_id,
            reference_date=date(2023, 11, 30),
            metrics=sample_monthly_metrics,
            id=2
        )
    ]


@pytest.fixture
def sample_company_aggregate(sample_company, sample_company_aliases, sample_company_metrics_snapshots):
    """Sample CompanyAggregate"""
    return CompanyAggregate(
        company=sample_company,
        company_aliases=sample_company_aliases,
        company_metrics_snapshots=sample_company_metrics_snapshots
    )


@pytest.fixture
def sample_company_orm(sample_company_id):
    """Sample Company ORM model"""
    return CompanyOrm(
        id=sample_company_id,
        external_id="sample-external-id",
        name="샘플회사",
        name_en="Sample Company",
        biz_categories=["Technology", "Software"],
        biz_tags=["startup", "ai", "saas"],
        founded_date=date(2020, 3, 15),
        employee_count=150,
        stage="Series B",
        biz_description="AI 기반 SaaS 플랫폼을 제공하는 스타트업",
        ipo_date=date(2023, 9, 20),
        total_investment=10000000000,
        origin_file_path="/data/sample_company.json"
    )


@pytest.fixture
def sample_company_alias_orm(sample_company_id):
    """Sample CompanyAlias ORM model"""
    return CompanyAliasOrm(
        company_id=sample_company_id,
        alias="샘플회사",
        alias_type="company_name",
        id=1
    )


@pytest.fixture
def sample_company_metrics_snapshot_orm(sample_company_id):
    """Sample CompanyMetricsSnapshot ORM model"""
    return CompanyMetricsSnapshotOrm(
        company_id=sample_company_id,
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


@pytest.fixture
def mock_openai_embedding_response():
    """Mock OpenAI embeddings API response"""
    response = Mock()
    response.data = [
        Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5]),
        Mock(embedding=[0.6, 0.7, 0.8, 0.9, 1.0])
    ]
    return response


@pytest.fixture
def sample_embedding_vectors():
    """Sample embedding vectors for testing"""
    return [
        [0.1, 0.2, 0.3] * 512,  # 1536 dimensions
        [0.4, 0.5, 0.6] * 512,  # 1536 dimensions
        [0.7, 0.8, 0.9] * 512   # 1536 dimensions
    ]


@pytest.fixture
def sample_forest_of_hyuksin_data():
    """Sample Forest of Hyuksin JSON data structure"""
    return {
        "base_company_info": {
            "data": {
                "seedCorp": {
                    "id": "forest-corp-123",
                    "corpNameKr": "포레스트회사",
                    "corpNameEn": "Forest Company",
                    "corpIntroKr": "숲에서 나는 혁신적인 회사",
                    "emplWholeVal": 200,
                    "foundAt": "2019-05-10",
                    "listingDate": "2023-11-15"
                },
                "seedCorpBiz": [
                    {"bizNameKr": "환경", "bizNameEn": "Environment"},
                    {"bizNameKr": "기술", "bizNameEn": "Technology"}
                ],
                "seedCorpTag": [
                    {"tagNameKr": "친환경", "tagNameEn": "Eco-friendly"},
                    {"tagNameKr": "지속가능", "tagNameEn": "Sustainable"}
                ]
            }
        },
        "products": [
            {"id": "prod1", "name": "에코앱"},
            {"id": "prod2", "name": "그린플랫폼"}
        ],
        "investment": {
            "data": [
                {
                    "level": "Series A",
                    "investAt": "2023-08-20",
                    "investmentAmount": 3000000000,
                    "investor": [
                        {"name": "그린벤처캐피탈"},
                        {"name": "환경투자펀드"}
                    ]
                }
            ],
            "totalInvestmentAmount": 3000000000,
            "lastInvestmentLevel": "Series A"
        },
        "mau": {
            "list": [
                {
                    "productId": "prod1",
                    "data": [
                        {
                            "value": 75000,
                            "growthRate": 25.0,
                            "referenceMonth": "2023-11"
                        }
                    ]
                }
            ]
        },
        "patent": {
            "list": [
                {
                    "level": "국제특허",
                    "title": "친환경 데이터 처리 시스템",
                    "registerAt": "2023-09-10"
                }
            ]
        },
        "finance": {
            "data": [
                {
                    "year": 2023,
                    "profit": 2000000000,
                    "operatingProfit": 1500000000,
                    "netProfit": 1200000000
                }
            ]
        },
        "organization": {
            "data": [
                {
                    "value": 200,
                    "growRate": 30.0,
                    "referenceMonth": "2023-11"
                }
            ]
        }
    }


@pytest.fixture
def mock_database_result():
    """Mock database query result"""
    result = Mock()
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    result.fetchall.return_value = []
    return result


@pytest.fixture
def mock_session_with_result(mock_async_session, mock_database_result):
    """Mock session that returns mock result"""
    mock_async_session.execute.return_value = mock_database_result
    return mock_async_session