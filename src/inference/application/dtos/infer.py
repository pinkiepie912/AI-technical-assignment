from datetime import date
from typing import Optional

from pydantic import BaseModel


class GetCompaniesParam(BaseModel):
    alias: str
    start_date: date
    end_date: Optional[date] = None
