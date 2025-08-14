import os

from dependency_injector.wiring import inject
from fastapi import APIRouter, Request, status

from containers import Container
from shared.exceptions import (
    BusinessLogicError,
    InternalServerError,
    ResourceNotFoundError,
    ValidationError,
)
from shared.swagger_responses import get_common_responses

from .dtos.file_process import FileProcessRequest, FileProcessResponse

router = APIRouter(
    prefix="/api/v1/enrichments",
    tags=["LLM RAG 데이터 처리 (Data Enrichment)"],
    responses=get_common_responses(),
)


@router.post(
    "/data-sources",
    response_model=FileProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="데이터 소스 파일 처리 및 저장",
    description="""
    지정된 경로의 데이터 파일을 읽어서 데이터베이스에 저장합니다.
    
    **지원 데이터 소스**:
    - FORESTOFHYUCKSIN: 혁신의숲 플랫폼 데이터
    
    **처리 과정**:
    1. 파일 경로 유효성 검증
    2. 데이터 소스 타입별 파싱
    3. 데이터베이스 저장
    4. 처리 결과 반환
    
    **참고사항**:
    - 파일 경로는 서버에서 접근 가능한 절대 경로여야 합니다
    - 동일한 파일을 중복 처리하면 기존 데이터가 업데이트됩니다
    """,
    response_description="데이터 처리 완료 정보 및 상태",
)
@inject
async def process_data_source_file(
    body: FileProcessRequest,
    request: Request,
) -> FileProcessResponse:
    """
    데이터 소스 파일을 처리하여 데이터베이스에 저장

    지정된 경로의 파일을 읽어서 데이터 소스 타입에 맞게 파싱한 후,
    데이터베이스에 저장합니다. 회사 정보, 뉴스 데이터 등을 처리할 수 있습니다.

    Args:
        body: 파일 처리 요청 정보
            - source: 데이터 소스 타입 (FORESTOFHYUCKSIN)
            - file_path: 처리할 파일의 절대 경로
        request: FastAPI 요청 객체 (컨테이너 접근용)
        company_info_writer: 회사 정보 작성 서비스 (의존성 주입)

    Returns:
        FileProcessResponse: 처리 결과 정보
            - message: 처리 결과 메시지
            - file_path: 처리된 파일 경로
            - status: 처리 상태 (success/failed)

    Raises:
        ValidationError: 요청 데이터 유효성 검증 실패
        ResourceNotFoundError: 파일을 찾을 수 없음
        BusinessLogicError: 파일 처리 로직 오류
        InternalServerError: 예상치 못한 서버 오류
    """
    try:
        # 파일 경로 유효성 검증
        await _validate_file_path(body.file_path)

        # 데이터 소스 설정
        container: Container = request.app.state.container
        container.reader_source_key.override(body.source.value)
        company_info_writer = container.company_info_writer()

        # 파일 처리 실행
        result = await company_info_writer.process_file(body.file_path)

        # 처리 결과 검증
        if not result.success:
            raise BusinessLogicError(
                detail="파일 처리에 실패했습니다.",
                details={
                    "file_path": body.file_path,
                    "source_type": body.source.value,
                    "error_message": result.message,
                },
            )

        return FileProcessResponse(
            message="파일이 성공적으로 처리되어 데이터베이스에 저장되었습니다.",
            file_path=body.file_path,
            status="success",
        )

    except (ValidationError, ResourceNotFoundError, BusinessLogicError):
        # 사용자 요청 관련 에러는 그대로 재발생
        raise
    except Exception as e:
        # 예상치 못한 에러는 InternalServerError로 변환
        raise InternalServerError(
            detail="데이터 소스 파일 처리 중 예상치 못한 오류가 발생했습니다.",
            details={
                "file_path": body.file_path,
                "source_type": body.source.value,
                "original_error": str(e),
            },
        )


async def _validate_file_path(file_path: str) -> None:
    """
    파일 경로의 유효성을 검증합니다.

    Args:
        file_path: 검증할 파일 경로

    Raises:
        ValidationError: 파일 경로가 유효하지 않은 경우
        ResourceNotFoundError: 파일이 존재하지 않는 경우
    """

    # 빈 경로 확인
    if not file_path or not file_path.strip():
        raise ValidationError(
            detail="파일 경로가 제공되지 않았습니다.", details={"file_path": file_path}
        )

    # 경로 보안 검증
    normalized_path = os.path.normpath(file_path)
    if ".." in normalized_path:
        raise ValidationError(
            detail="상위 디렉토리 접근은 허용되지 않습니다.",
            details={"provided_path": file_path, "normalized_path": normalized_path},
        )

    # 절대 경로 확인
    if not os.path.isabs(file_path):
        raise ValidationError(
            detail="절대 경로만 허용됩니다.",
            details={"provided_path": file_path, "is_absolute": False},
        )

    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise ResourceNotFoundError(
            resource="File", details={"file_path": file_path, "exists": False}
        )

    # 파일 타입 확인 (디렉토리가 아닌 일반 파일인지)
    if not os.path.isfile(file_path):
        raise ValidationError(
            detail="제공된 경로는 일반 파일이 아닙니다.",
            details={
                "file_path": file_path,
                "is_file": False,
                "is_directory": os.path.isdir(file_path),
            },
        )
