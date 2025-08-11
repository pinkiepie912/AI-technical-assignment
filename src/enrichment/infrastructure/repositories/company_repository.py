from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional, Sequence
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import ReadSessionManager, WriteSessionManager
from enrichment.application.dtos.company import (
    GetCompaniesMetricsSnapshotsPram,
)
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.vos.metrics import MonthlyMetrics
from enrichment.infrastructure.exceptions.repository_exception import (
    DuplicatedCompanyError,
)
from enrichment.infrastructure.orm.company import Company as CompanyOrm
from enrichment.infrastructure.orm.company_alias import CompanyAlias as CompanyAliasOrm
from enrichment.infrastructure.orm.company_snapshot import (
    CompanyMetricsSnapshot as CompanyMetricsSnapshotOrm,
)
from inference.application.dtos.infer import GetCompaniesParam


class CompanyRepository:
    def __init__(
        self,
        write_session_manager: WriteSessionManager,
        read_session_manager: ReadSessionManager,
    ):
        self.write_session_manager = write_session_manager
        self.read_session_manager = read_session_manager

    async def save(self, aggregate: CompanyAggregate) -> None:
        async with self.write_session_manager as session:
            stmt = select(CompanyOrm).where(
                CompanyOrm.external_id == aggregate.company.external_id
            )
            existing_company = (await session.execute(stmt)).scalar_one_or_none()
            if existing_company:
                raise DuplicatedCompanyError()

            company_orm = CompanyOrm(
                id=aggregate.company.id,
                external_id=aggregate.company.external_id,
                name=aggregate.company.name,
                name_en=aggregate.company.name_en,
                biz_categories=aggregate.company.industry,
                biz_tags=aggregate.company.tags,
                biz_description=aggregate.company.business_description,
                stage=aggregate.company.stage,
                total_investment=aggregate.company.total_investment,
                founded_date=aggregate.company.founded_date,
                ipo_date=aggregate.company.ipo_date,
                employee_count=aggregate.company.employee_count,
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

    async def get_companies(
        self, params_list: List[GetCompaniesParam]
    ) -> List[CompanyAggregate]:
        if not params_list:
            return []

        company_orms = []
        snapshot_orm_map = {}
        alias_orm_map = defaultdict(list)
        async with self.read_session_manager as session:
            aliases_map = await self._get_aliases_map_by(
                [param.alias for param in params_list], session
            )

            company_ids = []
            metrics_params = []
            for params in params_list:
                alias_orm = aliases_map.get(params.alias)
                if not alias_orm:
                    continue

                alias_orm_map[alias_orm.company_id].append(alias_orm)

                company_ids.append(alias_orm.company_id)
                metrics_params.append(
                    GetCompaniesMetricsSnapshotsPram(
                        company_id=alias_orm.company_id,
                        start_date=params.start_date,
                        end_date=params.end_date,
                    )
                )

            company_orms = await self._get_companies(company_ids, session=session)
            snapshot_orm_map = await self._get_companies_metrics_snapshots(
                metrics_params, session=session
            )

        aggregates = []
        for company_orm in company_orms:
            aggregates.append(
                self._create_company_aggregate(
                    company_orm=company_orm,
                    alias_orms=alias_orm_map.get(company_orm.id, []),
                    snapshot_orm=snapshot_orm_map.get(company_orm.id, []),
                )
            )
        return aggregates

    async def _get_aliases_map_by(
        self, aliases: List[str], session: Optional[AsyncSession] = None
    ) -> Dict[str, CompanyAliasOrm]:
        if not aliases:
            return {}

        query = select(CompanyAliasOrm).where(CompanyAliasOrm.alias.in_(aliases))

        if session:
            orms = (await session.execute(query)).scalars().all()
        else:
            async with self.read_session_manager as session:
                orms = (await session.execute(query)).scalars().all()

        alias_map = {}
        for row in orms:
            alias_map[row.alias] = row
        return alias_map

    async def _get_companies(
        self, company_ids: List[UUID], session: Optional[AsyncSession] = None
    ) -> Sequence[CompanyOrm]:
        if not company_ids:
            return []

        query = select(CompanyOrm).where(CompanyOrm.id.in_(company_ids))

        if session:
            ext = await session.execute(query)
        else:
            async with self.read_session_manager as session:
                ext = await session.execute(query)

        return ext.scalars().all()

    async def _get_companies_metrics_snapshots(
        self,
        params: List[GetCompaniesMetricsSnapshotsPram],
        session: Optional[AsyncSession] = None,
    ) -> Dict[UUID, List[CompanyMetricsSnapshotOrm]]:
        if not params:
            return {}

        conditions = []
        for param in params:
            end_date = param.end_date or date.today()
            conditions.append(
                and_(
                    CompanyMetricsSnapshotOrm.company_id == param.company_id,
                    CompanyMetricsSnapshotOrm.reference_date >= param.start_date,
                    CompanyMetricsSnapshotOrm.reference_date <= end_date,
                )
            )

        query = (
            select(CompanyMetricsSnapshotOrm)
            .where(or_(*conditions))
            .order_by(CompanyMetricsSnapshotOrm.reference_date.desc())
        )

        if session:
            ext = await session.execute(query)
        else:
            async with self.read_session_manager as session:
                ext = await session.execute(query)

        orms = ext.scalars().all()
        result = defaultdict(list)
        for orm in orms:
            result[orm.company_id].append(orm)

        return result

    def _create_company_aggregate(
        self,
        company_orm: CompanyOrm,
        alias_orms: List[CompanyAliasOrm],
        snapshot_orm: List[CompanyMetricsSnapshotOrm],
    ) -> CompanyAggregate:
        return CompanyAggregate(
            company=self._create_company_from(company_orm),
            company_aliases=[self._create_alias_from(alias) for alias in alias_orms],
            company_metrics_snapshots=[
                self._create_snapshots_from(snapshot) for snapshot in snapshot_orm
            ],
        )

    def _create_company_from(self, orm: CompanyOrm) -> Company:
        return Company(
            id=orm.id,
            external_id=orm.external_id,
            name=orm.name,
            name_en=orm.name_en or "",
            industry=orm.biz_categories or [],
            tags=orm.biz_tags or [],
            founded_date=orm.founded_date,
            employee_count=orm.employee_count,
            investment_total=orm.total_investment,
            stage=orm.stage or "",
            business_description=orm.biz_description or "",
            ipo_date=orm.ipo_date,
            total_investment=orm.total_investment,
            origin_file_path=orm.origin_file_path or "",
        )

    def _create_alias_from(self, alias_orm: CompanyAliasOrm) -> CompanyAlias:
        return CompanyAlias(
            company_id=alias_orm.company_id,
            alias=alias_orm.alias,
            alias_type=alias_orm.alias_type,
            id=alias_orm.id,
        )

    def _create_snapshots_from(
        self, snapshot_orm: CompanyMetricsSnapshotOrm
    ) -> CompanyMetricsSnapshot:
        monthly_metrics = MonthlyMetrics.model_validate(snapshot_orm.metrics)
        return CompanyMetricsSnapshot(
            company_id=snapshot_orm.company_id,
            reference_date=snapshot_orm.reference_date,
            metrics=monthly_metrics,
            id=snapshot_orm.id,
        )
