import json
from typing import Any, Dict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import ValidationError as PydanticValidationError

from containers import Container
from inference.application.services.talent_infer import TalentInference
from inference.controllers.dtos.talent_infer import TalentProfile
from inference.controllers.dtos.talent_infer_response import TalentInferResponse
from shared.exceptions import (
    FileProcessingError,
    InternalServerError,
    ValidationError,
)
from shared.swagger_responses import get_file_upload_responses

router = APIRouter(
    prefix="/api/v1/inferences",
    tags=["인재 추론 (Talent Inference)"],
    responses=get_file_upload_responses(),
)


@router.post(
    "/talent-profiles/analyze",
    status_code=status.HTTP_200_OK,
    summary="인재 프로필 분석 및 추론",
    description="업로드된 JSON 파일의 인재 정보를 분석하여 경험 태그를 추론합니다.",
    response_description="분석된 인재 프로필 정보 및 추론된 경험 태그",
)
@inject
async def analyze_talent_profile(
    file: UploadFile = File(
        ..., description="인재 정보가 담긴 JSON 파일", media_type="application/json"
    ),
    talent_inference_service: TalentInference = Depends(
        Provide[Container.talent_inference_service]
    ),
) -> TalentInferResponse:
    """
    인재 프로필 분석 및 경험 태그 추론

    업로드된 JSON 파일을 분석하여 인재의 경력, 교육, 스킬 정보를 기반으로
    "성장기스타트업 경험", "대규모 회사 경험", "리더십" 등의 경험 태그를 추론합니다.

    Args:
        file: 인재 프로필 정보가 담긴 JSON 파일
            - 필수 필드: firstName, lastName, positions, educations
            - 선택 필드: skills, headline, summary, website 등
        talent_inference_service: 인재 추론 서비스 (의존성 주입)

    Returns:
        Dict[str, Any]: 분석 결과 및 추론된 경험 태그
            - experience_tags: 추론된 경험 태그 리스트
            - competency_tags: 추론된 역량 태그 리스트
            - inferences: 추론된 인재 정보

    Raises:
        FileProcessingError: 파일 형식이 잘못되었거나 처리할 수 없는 경우
        ValidationError: 입력 데이터가 요구사항을 만족하지 않는 경우
        InternalServerError: 추론 과정에서 예상치 못한 오류가 발생한 경우
    """
    try:
        # 파일 유효성 검증
        await _validate_uploaded_file(file)

        # 파일 내용 읽기 및 파싱
        talent_data = await _parse_json_file(file)

        # TalentProfile 모델 검증
        talent_profile = await _validate_talent_profile(talent_data)

        # 인재 정보 추론 실행
        inference_result = await talent_inference_service.inference(talent_profile)

        return inference_result

    except (FileProcessingError, ValidationError):
        # 사용자 입력 관련 에러는 그대로 재발생
        raise
    except Exception as e:
        # 예상치 못한 에러는 InternalServerError로 변환
        raise InternalServerError(
            detail="인재 프로필 분석 중 예상치 못한 오류가 발생했습니다.",
            details={"original_error": str(e)},
        )


async def _validate_uploaded_file(file: UploadFile) -> None:
    """
    업로드된 파일의 유효성을 검증합니다.

    Args:
        file: 업로드된 파일 객체

    Raises:
        FileProcessingError: 파일이 유효하지 않은 경우
    """
    # 파일명 존재 여부 확인
    if not file.filename:
        raise FileProcessingError(
            detail="파일명이 제공되지 않았습니다.", details={"filename": None}
        )

    # 파일 확장자 검증
    if not file.filename.lower().endswith(".json"):
        raise FileProcessingError(
            detail="지원하지 않는 파일 형식입니다. JSON 파일만 업로드 가능합니다.",
            details={
                "provided_filename": file.filename,
                "supported_formats": [".json"],
            },
        )

    # 파일 크기 검증 (10MB 제한)
    if hasattr(file, "size") and file.size and file.size > 10 * 1024 * 1024:
        raise FileProcessingError(
            detail="파일 크기가 너무 큽니다. 최대 10MB까지 업로드 가능합니다.",
            details={"file_size": file.size, "max_size": 10 * 1024 * 1024},
        )


async def _parse_json_file(file: UploadFile) -> Dict[str, Any]:
    """
    JSON 파일을 읽고 파싱합니다.

    Args:
        file: 업로드된 JSON 파일

    Returns:
        Dict[str, Any]: 파싱된 JSON 데이터

    Raises:
        FileProcessingError: 파일 읽기 또는 파싱에 실패한 경우
    """
    try:
        # 파일 내용 읽기
        file_content = await file.read()

        if not file_content:
            raise FileProcessingError(
                detail="업로드된 파일이 비어있습니다.", details={"file_size": 0}
            )

    except Exception as e:
        raise FileProcessingError(
            detail="파일 읽기 중 오류가 발생했습니다.", details={"read_error": str(e)}
        )

    try:
        # UTF-8 디코딩
        content_str = file_content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise FileProcessingError(
            detail="파일 인코딩이 올바르지 않습니다. UTF-8 인코딩이 필요합니다.",
            details={"encoding_error": str(e)},
        )

    try:
        # JSON 파싱
        talent_data = json.loads(content_str)
    except json.JSONDecodeError as e:
        raise FileProcessingError(
            detail="유효하지 않은 JSON 형식입니다.",
            details={
                "json_error": str(e),
                "line": getattr(e, "lineno", None),
                "column": getattr(e, "colno", None),
            },
        )

    return talent_data


async def _validate_talent_profile(talent_data: Dict[str, Any]) -> TalentProfile:
    """
    인재 프로필 데이터를 검증하고 TalentProfile 모델로 변환합니다.

    Args:
        talent_data: 파싱된 JSON 데이터

    Returns:
        TalentProfile: 검증된 인재 프로필 모델

    Raises:
        ValidationError: 데이터 검증에 실패한 경우
    """
    try:
        return TalentProfile.model_validate(talent_data)
    except PydanticValidationError as e:
        # Pydantic 검증 오류를 사용자 친화적인 메시지로 변환
        field_errors = []
        for error in e.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors.append(f"{field_path}: {error['msg']}")

        raise ValidationError(
            detail="인재 프로필 데이터 형식이 올바르지 않습니다.",
            details={"field_errors": field_errors, "error_count": len(field_errors)},
        )
