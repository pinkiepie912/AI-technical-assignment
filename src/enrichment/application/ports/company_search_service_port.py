from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate


@dataclass(frozen=True)
class CompanySearchParam:
    alias: str
    start_date: date
    end_date: Optional[date] = None


class CompanySearchServicePort(ABC):
    """
    Bounded Context Port for Company Search Service.
    """

    @abstractmethod
    async def get_companies(
        self, params: List[CompanySearchParam]
    ) -> List[CompanyAggregate]: ...
