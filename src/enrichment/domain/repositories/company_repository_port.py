from abc import ABC, abstractmethod
from typing import List

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.specs.company_spec import CompanySearchParam


class CompanyRepositoryPort(ABC):
    """Interface for the Company Repository Port."""

    @abstractmethod
    async def save(self, aggregate: CompanyAggregate) -> None: ...

    @abstractmethod
    async def get_companies(
        self, params: List[CompanySearchParam]
    ) -> List[CompanyAggregate]: ...
