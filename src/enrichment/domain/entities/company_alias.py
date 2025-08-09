from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

__all__ = ["CompanyAlias", "CompanyAliasCreateParams"]


class CompanyAliasCreateParams(BaseModel):
    company_id: UUID
    alias: str
    alias_type: str

    model_config = ConfigDict(frozen=True)


class CompanyAlias(BaseModel):
    company_id: UUID
    alias: str
    alias_type: str
    id: Optional[int] = None

    @staticmethod
    def of(params: CompanyAliasCreateParams) -> CompanyAlias:
        return CompanyAlias(
            company_id=params.company_id,
            alias=params.alias,
            alias_type=params.alias_type,
        )
