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
    """
    회사 별칭 도메인 엔티티 - 회사를 식별할 수 있는 다양한 이름들을 관리
    회사명, 제품명 등을 포함하며 CompanyAggregate의 구성 요소
    """

    company_id: UUID  # 소속 회사 ID
    alias: str  # 별칭 (회사명 또는 제품명)
    alias_type: str  # 별칭 타입 구분
    id: Optional[int] = None  # 데이터베이스 기본키 (생성 후 할당)

    @staticmethod
    def of(params: CompanyAliasCreateParams) -> CompanyAlias:
        return CompanyAlias(
            company_id=params.company_id,
            alias=params.alias,
            alias_type=params.alias_type,
        )
