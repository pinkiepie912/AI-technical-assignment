from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CompanySearchParam:
    alias: str
    start_date: date
    end_date: Optional[date] = None
