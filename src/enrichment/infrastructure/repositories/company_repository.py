from db.db import WriteSessionManager
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import (
    CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm,
)


class CompanyRepository:
    def __init__(self, session_manager: WriteSessionManager):
        self.session_manager = session_manager

    async def save(self, aggregate: CompanyAggregate) -> None:
        async with self.session_manager as session:
            company_orm = CompanyOrm(
                id=aggregate.company.id,
                name=aggregate.company.name,
                name_en=aggregate.company.name_en,
                biz_categories=(
                    aggregate.company.industry.split(", ")
                    if aggregate.company.industry and aggregate.company.industry.strip()
                    else []
                ),
                total_investment=aggregate.company.total_investment,
                founded_date=aggregate.company.founded_date,
                ipo_date=aggregate.company.ipo_date,
                origin_file_path=aggregate.company.origin_file_path,
            )
            session.add(company_orm)

            for alias in aggregate.company_aliases:
                alias_orm = CompanyAliasOrm(
                    company_id=alias.company_id,
                    alias=alias.alias,
                    alias_type=alias.alias_type,
                )
                session.add(alias_orm)

            for snapshot in aggregate.company_metrics_snapshots:
                snapshot_orm = CompanyMetricsSnapshotOrm(
                    company_id=snapshot.company_id,
                    reference_date=snapshot.reference_date,
                    metrics=snapshot.metrics.model_dump(mode="json"),
                )
                session.add(snapshot_orm)
