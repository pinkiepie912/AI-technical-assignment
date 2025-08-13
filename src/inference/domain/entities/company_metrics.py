from dataclasses import dataclass
from typing import List


@dataclass
class PatentSummary:
    level: str
    title: str


@dataclass
class MAUSummary:
    product_name: str
    value: int
    growth_rate: float


@dataclass
class MetricsSummary:
    people_count: int
    people_growth_rate: float

    profit: int
    net_profit: int
    profit_growth_rate: float
    net_profit_growth_rate: float

    investment_amount: int
    investors: List[str]
    levels: List[str]

    patents: List[PatentSummary]
    maus: List[MAUSummary]
