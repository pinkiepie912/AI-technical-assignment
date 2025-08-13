"""
공통 Swagger 응답 문서화

모든 API에서 재사용할 수 있는 Swagger 응답 정의를 제공합니다.
"""

from typing import Any, Dict, Union

from .exceptions import ErrorResponse


def get_common_responses() -> Dict[Union[int, str], Dict[str, Any]]:
    """
    공통 HTTP 에러 응답 정의

    모든 API에서 발생할 수 있는 공통 에러 응답들을 정의합니다.

    Returns:
        Dict: FastAPI responses 딕셔너리
    """
    return {
        400: {
            "model": ErrorResponse,
            "description": "잘못된 요청 - 요청 형식이나 파라미터가 올바르지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "message": "Invalid request format",
                            "code": "BAD_REQUEST",
                            "details": None,
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/example",
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "리소스를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "message": "Resource not found",
                            "code": "RESOURCE_NOT_FOUND",
                            "details": None,
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/example",
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "유효성 검증 실패 - 입력 데이터가 요구사항을 만족하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "message": "Validation failed",
                            "code": "VALIDATION_ERROR",
                            "details": {"field_errors": ["Field 'name' is required"]},
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/example",
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "내부 서버 오류 - 서버에서 예상치 못한 오류가 발생함",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "message": "Internal server error",
                            "code": "INTERNAL_SERVER_ERROR",
                            "details": None,
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/example",
                    }
                }
            },
        },
    }


def get_file_upload_responses() -> Dict[Union[int, str], Dict[str, Any]]:
    """
    파일 업로드 관련 추가 에러 응답

    Returns:
        Dict: 파일 업로드 특화 응답 딕셔너리
    """
    responses = get_common_responses()
    responses.update(
        {
            413: {
                "model": ErrorResponse,
                "description": "파일 크기가 너무 큼",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "error": {
                                "message": "File size too large",
                                "code": "PAYLOAD_TOO_LARGE",
                                "details": {"max_size": "10MB"},
                            },
                            "timestamp": "2024-01-01T12:00:00Z",
                            "path": "/api/v1/upload",
                        }
                    }
                },
            },
            415: {
                "model": ErrorResponse,
                "description": "지원하지 않는 파일 형식",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "error": {
                                "message": "Unsupported file format",
                                "code": "UNSUPPORTED_MEDIA_TYPE",
                                "details": {"supported_formats": [".json"]},
                            },
                            "timestamp": "2024-01-01T12:00:00Z",
                            "path": "/api/v1/upload",
                        }
                    }
                },
            },
        }
    )
    return responses

