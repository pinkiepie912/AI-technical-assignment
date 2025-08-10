from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GetCompaniesMetricsSnapshotsPram(BaseModel):
    company_id: UUID
    start_date: date
    end_date: Optional[date] = None
