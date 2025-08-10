import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Union
from uuid import UUID, uuid4

from enrichment.application.exceptions.reader_exception import (
    ReaderEncodingError,
    ReaderInvalidFormatError,
    ReaderValidationError,
)
from enrichment.application.interfaces.reader_interface import JSONDataReader
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.entities.company import Company, CompanyCreateParams
from enrichment.domain.entities.company_alias import (
    CompanyAlias,
    CompanyAliasCreateParams,
)
from enrichment.domain.entities.company_metrics_snapshot import (
    CompanyMetricSnapshotCreateParams,
    CompanyMetricsSnapshot,
)
from enrichment.domain.vos.metrics import (
    MAU,
    Finance,
    Investment,
    MonthlyMetrics,
    Organization,
    Patent,
)

from ..dtos.forest_of_hyuksin import ForestOfHyuksinCompanyData


class ForestOfHyuksinReader(JSONDataReader):
    def read(self, file_path: Union[str, Path]) -> CompanyAggregate:
        file_path = Path(file_path)

        self.validate_file_exists(file_path)

        try:
            with file_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)

        except json.JSONDecodeError as e:
            raise ReaderInvalidFormatError(str(file_path), "JSON", str(e))

        except UnicodeDecodeError as e:
            raise ReaderEncodingError(str(file_path), "UTF-8", str(e))

        except Exception as e:
            raise ReaderInvalidFormatError(
                str(file_path), "JSON", f"Unexpected error: {e}"
            )

        try:
            company_data = ForestOfHyuksinCompanyData.model_validate(json_data)
            return self._to_aggregate(company_data, file_path)

        except Exception as e:
            raise ReaderValidationError(str(file_path), "ForestOfHyuksin", str(e))

    def _to_aggregate(
        self, data: ForestOfHyuksinCompanyData, path: Path
    ) -> CompanyAggregate:
        company_id = uuid4()
        company_aliases = self._create_company_aliases(company_id, data)
        company_metrics_snapshots = self._create_company_metrics_snapshots(
            company_id, data
        )

        company = self._create_company(
            company_id, data, company_aliases, company_metrics_snapshots, path
        )

        return CompanyAggregate.of(
            company=company,
            company_aliases=company_aliases,
            company_metrics_snapshots=company_metrics_snapshots,
        )

    def _create_company(
        self,
        company_id: UUID,
        data: ForestOfHyuksinCompanyData,
        company_aliases: List[CompanyAlias],
        company_metrics_snapshots: List[CompanyMetricsSnapshot],
        path: Path,
    ) -> Company:
        params = CompanyCreateParams(
            name=data.base_company_info.data.seedCorp.corpNameKr,
            name_en=data.base_company_info.data.seedCorp.corpNameEn or None,
            industry=(
                ", ".join(
                    [biz.bizNameKr for biz in data.base_company_info.data.seedCorpBiz]
                )
                if data.base_company_info.data.seedCorpBiz
                else None
            ),
            employee_count=data.base_company_info.data.seedCorp.emplWholeVal,
            investment_total=(
                data.investment.totalInvestmentAmount if data.investment else None
            ),
            stage=data.investment.lastInvestmentLevel if data.investment else None,
            business_description=data.base_company_info.data.seedCorp.corpIntroKr
            or None,
            founded_date=(
                datetime.strptime(
                    data.base_company_info.data.seedCorp.foundAt, "%Y-%m-%d"
                ).date()
                if data.base_company_info.data.seedCorp.foundAt
                else None
            ),
            ipo_date=(
                datetime.strptime(
                    data.base_company_info.data.seedCorp.listingDate, "%Y-%m-%d"
                ).date()
                if data.base_company_info.data.seedCorp.listingDate
                else None
            ),
            origin_file_path=str(path.absolute()),
            alias_params=[
                CompanyAliasCreateParams(
                    company_id=company_id,
                    alias=alias.alias,
                    alias_type=alias.alias_type,
                )
                for alias in company_aliases
            ],
            snapshot_params=[
                CompanyMetricSnapshotCreateParams(
                    company_id=snapshot.company_id,
                    reference_date=snapshot.reference_date,
                    metrics=snapshot.metrics,
                )
                for snapshot in company_metrics_snapshots
            ],
        )
        company = Company.of(params)
        company.id = company_id
        return company

    def _create_company_aliases(
        self, company_id: UUID, data: ForestOfHyuksinCompanyData
    ) -> List[CompanyAlias]:
        aliases = set()

        # Add company names
        if data.base_company_info.data.seedCorp.corpNameKr:
            aliases.add(data.base_company_info.data.seedCorp.corpNameKr)
        if data.base_company_info.data.seedCorp.corpNameEn:
            aliases.add(data.base_company_info.data.seedCorp.corpNameEn)

        # Add product names
        if data.products:
            for product in data.products:
                if product.name:
                    aliases.add(product.name)

        return [
            CompanyAlias.of(
                CompanyAliasCreateParams(
                    company_id=company_id, alias=alias, alias_type="name"
                )
            )
            for alias in aliases
        ]

    def _create_company_metrics_snapshots(
        self, company_id: UUID, data: ForestOfHyuksinCompanyData
    ) -> List[CompanyMetricsSnapshot]:
        monthly_metrics: Dict[date, MonthlyMetrics] = defaultdict(
            lambda: MonthlyMetrics(
                mau=[], patents=[], finance=[], investments=[], organizations=[]
            )
        )

        self._collect_all_metrics(monthly_metrics, data)

        return [
            CompanyMetricsSnapshot.of(
                CompanyMetricSnapshotCreateParams(
                    company_id=company_id,
                    reference_date=ref_date,
                    metrics=metrics,
                )
            )
            for ref_date, metrics in monthly_metrics.items()
        ]

    def _collect_all_metrics(
        self,
        monthly_metrics: Dict[date, MonthlyMetrics],
        data: ForestOfHyuksinCompanyData,
    ) -> None:
        # Collect MAU metrics
        if data.mau and data.products:
            product_name_map = {p.id: p.name for p in data.products}
            for mau_product in data.mau.list:
                for mau_data in mau_product.data:
                    try:
                        ref_date = (
                            datetime.strptime(mau_data.referenceMonth, "%Y-%m")
                            .date()
                            .replace(day=1)
                        )
                        product_name = product_name_map.get(mau_product.productId, "")
                        monthly_metrics[ref_date].mau.append(
                            MAU(
                                product_id=mau_product.productId,
                                product_name=product_name,
                                value=mau_data.value,
                                growthRate=mau_data.growthRate,
                                date=ref_date,
                            )
                        )
                    except (ValueError, TypeError):
                        continue

        # Collect Patent metrics
        if data.patent:
            for patent_item in data.patent.list:
                try:
                    ref_date = (
                        datetime.strptime(patent_item.registerAt, "%Y-%m-%d")
                        .date()
                        .replace(day=1)
                    )
                    monthly_metrics[ref_date].patents.append(
                        Patent(
                            level=patent_item.level,
                            title=patent_item.title,
                            date=ref_date,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        # Collect Finance metrics (annual -> December)
        if data.finance:
            for finance_data in data.finance.data:
                ref_date = date(finance_data.year, 12, 1)
                monthly_metrics[ref_date].finance.append(
                    Finance(
                        year=finance_data.year,
                        profit=finance_data.profit,
                        netProfit=finance_data.netProfit,
                        operatingProfit=finance_data.operatingProfit,
                    )
                )

        # Collect Investment metrics
        if data.investment and data.investment.data:
            for investment_data in data.investment.data:
                if not self._is_valid_investment_data(investment_data):
                    continue

                invest_at_str = investment_data.get("investAt")
                if not invest_at_str:
                    continue

                try:
                    ref_date = (
                        datetime.strptime(invest_at_str, "%Y-%m-%d")
                        .date()
                        .replace(day=1)
                    )
                    investors = self._extract_investor_names(
                        investment_data.get("investor", [])
                    )
                    monthly_metrics[ref_date].investments.append(
                        Investment(
                            level=investment_data.get("level", ""),
                            date=ref_date,
                            amount=investment_data.get("investmentAmount", 0),
                            investors=investors,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        # Collect Organization metrics
        if data.organization:
            for org_data in data.organization.data:
                try:
                    ref_date = (
                        datetime.strptime(org_data.referenceMonth, "%Y-%m")
                        .date()
                        .replace(day=1)
                    )
                    monthly_metrics[ref_date].organizations.append(
                        Organization(
                            name="employee",
                            date=ref_date,
                            people_count=(
                                org_data.value if org_data.value is not None else 0
                            ),
                            growth_rate=(
                                org_data.growRate
                                if org_data.growRate is not None
                                else 0.0
                            ),
                        )
                    )
                except (ValueError, TypeError):
                    continue

    def _is_valid_investment_data(self, investment_data: dict) -> bool:
        """Validate investment data structure and required fields."""

        invest_at = investment_data.get("investAt")
        return invest_at is not None and isinstance(invest_at, str)

    def _extract_investor_names(self, investor_list: List[dict]) -> List[str]:
        """Extract investor names from investor list with validation."""

        investors = []
        for investor in investor_list:
            if isinstance(investor, dict):
                name = investor.get("name")
                if name and isinstance(name, str):
                    investors.append(name)
        return investors
