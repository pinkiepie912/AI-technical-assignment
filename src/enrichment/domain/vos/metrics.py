from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MAU(BaseModel):
    product_id: str
    product_name: str
    value: int
    date: date
    growthRate: Optional[float] = None

    model_config = ConfigDict(frozen=True)


class Patent(BaseModel):
    level: str
    title: str
    date: date

    model_config = ConfigDict(frozen=True)


class Finance(BaseModel):
    year: int
    profit: int
    operatingProfit: int
    netProfit: Optional[int] = None

    model_config = ConfigDict(frozen=True)


class Investment(BaseModel):
    level: str
    date: date
    amount: int
    investors: List[str]

    model_config = ConfigDict(frozen=True)


class Organization(BaseModel):
    name: str
    date: date
    people_count: int
    growth_rate: float

    model_config = ConfigDict(frozen=True)


class MonthlyMetrics(BaseModel):
    mau: List[MAU]
    patents: List[Patent]
    finance: List[Finance]
    investments: List[Investment]
    organizations: List[Organization]

    model_config = ConfigDict(frozen=True)
