from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="에러 상세 정보")
