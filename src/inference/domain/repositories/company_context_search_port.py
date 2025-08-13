from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from inference.domain.aggregates.company_context import CompanyContext


@dataclass(frozen=True)
class CompanySearchContextParam:
    alias: str
    start_date: date
    end_date: Optional[date] = None


class CompanyContextSearchPort(ABC):
    @abstractmethod
    async def search(
        self, params: List[CompanySearchContextParam]
    ) -> List[CompanyContext]: ...
