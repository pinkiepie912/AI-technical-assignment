from typing import List

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.infrastructure.repositories.company_repository import CompanyRepository
from inference.application.dtos.infer import GetCompaniesParam

__all__ = ["CompanyInfoReader"]


class CompanyInfoReader:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    async def get_company_info(
        self,
        params: List[GetCompaniesParam],
    ) -> List[CompanyAggregate]:
        aggregate = await self.repository.get_companies(params)
        return aggregate
