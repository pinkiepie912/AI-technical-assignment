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

    patents: List[PatentSummary]
    maus: List[MAUSummary]

    def is_empty(self) -> bool:
        """메트릭 요약 정보가 비어있는지 확인"""
        return (
            self.people_count == 0
            and self.people_growth_rate == 0.0
            and self.profit == 0
            and self.net_profit == 0
            and self.profit_growth_rate == 0.0
            and self.net_profit_growth_rate == 0.0
            and self.investment_amount == 0
            and not self.investors
            and not self.patents
            and not self.maus
        )
