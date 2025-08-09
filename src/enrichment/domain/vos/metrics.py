from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class MAU:
    product_id: str
    product_name: str
    value: int
    date: date
    growthRate: Optional[float] = None


@dataclass
class Patent:
    level: str
    title: str
    date: date


@dataclass
class Finance:
    year: int
    profit: int
    operatingProfit: int
    netProfit: Optional[int] = None


@dataclass
class Investment:
    level: str
    date: date
    amount: int
    investors: List[str]


@dataclass
class Organization:
    name: str
    date: date
    people_count: int
    growth_rate: float


@dataclass
class MonthlyMetrics:
    mau: List[MAU]
    patents: List[Patent]
    finance: List[Finance]
    investments: List[Investment]
    organizations: List[Organization]
