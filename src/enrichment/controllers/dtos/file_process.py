from enum import StrEnum, auto

from pydantic import BaseModel, Field

__all__ = ["FileProcessRequest", "FileProcessResponse"]


class SourceType(StrEnum):
    FORESTOFHYUCKSIN = auto()


class FileProcessRequest(BaseModel):
    source: SourceType
    file_path: str = Field(
        description="처리할 파일의 경로", examples=["/path/to/data/user_data.json"]
    )


class FileProcessResponse(BaseModel):
    message: str = Field(..., description="처리 결과 메시지")
    file_path: str = Field(..., description="처리된 파일 경로")
    status: str = Field(..., description="처리 상태")
