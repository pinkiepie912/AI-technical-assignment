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
    """
    try:
        # 파일 경로 유효성 검증
        # await _validate_file_path(body.file_path)

        # 데이터 소스 설정
        container: Container = request.app.state.container
        container.reader_source_key.override(body.source.value)

        # container에서 사용하는 db.db.engine_with_pgvector의 async context manager로
        # db 엔진을 생성하기 때문에, db engine을 주입받는 하위 객체들은 모두 async mode가 된다.
        # Selector를 통해 Parameter로 reader를 선택하게 하기 위해서는 writer 객체를 await으로 가져와야 한다.
        company_info_writer = await container.company_info_writer()  # type: ignore

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
