from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional
from uuid import UUID

__all__ = ["CompanyAlias", "CompanyAliasCreateParams"]


@dataclass
class CompanyAliasCreateParams:
    company_id: UUID
    alias: str
    alias_type: str


@dataclass
class CompanyAlias:
    company_id: UUID
    alias: str
    alias_type: str
    id: Optional[int] = None

    @staticmethod
    def of(params: CompanyAliasCreateParams) -> CompanyAlias:
        return CompanyAlias(
            **asdict(params),
        )
