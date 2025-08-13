from typing import List

from enrichment.application.ports.company_search_service_port import (
    CompanySearchParam,
    CompanySearchServicePort,
)
from enrichment.application.ports.text_embedding_client_port import (
    TextEmbeddingClientPort,
)
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.repositories.company_repository_port import CompanyRepositoryPort
from enrichment.domain.specs.company_spec import CompanySearchParam

__all__ = ["CompanyInfoReader"]


class CompanyInfoReader(CompanySearchServicePort):
    def __init__(
        self,
        repository: CompanyRepositoryPort,
        embedding_client=TextEmbeddingClientPort,
    ):
        self.repository = repository

    async def get_companies(
        self,
        params: List[CompanySearchParam],
    ) -> List[CompanyAggregate]:
        companies = await self.repository.get_companies(
            [
                CompanySearchParam(
                    alias=row.alias, start_date=row.start_date, end_date=row.end_date
                )
                for row in params
            ]
        )
        return companies
