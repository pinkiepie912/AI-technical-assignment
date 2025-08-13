"""
공통 예외 처리 및 에러 응답 모델

이 모듈은 FastAPI 애플리케이션 전체에서 사용할 일관된 예외 처리와
에러 응답 형식을 제공합니다.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """에러 상세 정보 모델"""

    message: str = Field(..., description="에러 메시지")
    code: str = Field(..., description="에러 코드")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 에러 정보")


class ErrorResponse(BaseModel):
    """표준 에러 응답 모델"""

    success: bool = Field(False, description="요청 성공 여부")
    error: ErrorDetail = Field(..., description="에러 정보")
    timestamp: str = Field(..., description="에러 발생 시간 (ISO 8601)")
    path: str = Field(..., description="요청 경로")


class ValidationError(HTTPException):
    """유효성 검증 에러"""

    def __init__(
        self,
        detail: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": detail, "code": "VALIDATION_ERROR", "details": details},
        )


class BusinessLogicError(HTTPException):
    """비즈니스 로직 에러"""

    def __init__(
        self,
        detail: str = "Business logic error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": detail,
                "code": "BUSINESS_LOGIC_ERROR",
                "details": details,
            },
        )


class ResourceNotFoundError(HTTPException):
    """리소스 미발견 에러"""

    def __init__(
        self, resource: str = "Resource", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"{resource} not found",
                "code": "RESOURCE_NOT_FOUND",
                "details": details,
            },
        )


class InternalServerError(HTTPException):
    """내부 서버 에러"""

    def __init__(
        self,
        detail: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": detail,
                "code": "INTERNAL_SERVER_ERROR",
                "details": details,
            },
        )


class FileProcessingError(HTTPException):
    """파일 처리 에러"""

    def __init__(
        self,
        detail: str = "File processing failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": detail,
                "code": "FILE_PROCESSING_ERROR",
                "details": details,
            },
        )


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 예외 처리 핸들러

    모든 HTTP 예외를 일관된 형식으로 변환하여 응답합니다.

    Args:
        request: FastAPI 요청 객체
        exc: 발생한 HTTP 예외

    Returns:
        JSONResponse: 표준화된 에러 응답
    """
    from datetime import datetime

    # 예외 세부사항이 딕셔너리인 경우 (커스텀 예외)
    if isinstance(exc.detail, dict):
        error_detail = ErrorDetail(
            message=exc.detail.get("message", "An error occurred"),
            code=exc.detail.get("code", "UNKNOWN_ERROR"),
            details=exc.detail.get("details"),
        )
    else:
        # 일반 문자열 detail인 경우
        error_detail = ErrorDetail(
            message=str(exc.detail),
            code=_get_error_code_from_status(exc.status_code),
            details=None,
        )

    error_response = ErrorResponse(
        success=False,
        error=error_detail,
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    일반 예외 처리 핸들러

    HTTP 예외가 아닌 모든 예외를 500 에러로 변환합니다.

    Args:
        request: FastAPI 요청 객체
        exc: 발생한 일반 예외

    Returns:
        JSONResponse: 표준화된 에러 응답
    """
    from datetime import datetime

    error_detail = ErrorDetail(
        message="Internal server error",
        code="INTERNAL_SERVER_ERROR",
        details={"original_error": str(exc)} if str(exc) else None,
    )

    error_response = ErrorResponse(
        success=False,
        error=error_detail,
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def _get_error_code_from_status(status_code: int) -> str:
    """상태 코드에서 에러 코드 추출"""
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        410: "GONE",
        411: "LENGTH_REQUIRED",
        412: "PRECONDITION_FAILED",
        413: "PAYLOAD_TOO_LARGE",
        414: "URI_TOO_LONG",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        501: "NOT_IMPLEMENTED",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }
    return error_codes.get(status_code, "UNKNOWN_ERROR")

