from fastapi import APIRouter, HTTPException, Request, status

from containers import Container

from .dtos.error_response import ErrorResponse
from .dtos.file_process import FileProcessRequest, FileProcessResponse

router = APIRouter(
    prefix="/api/v1/enrichments",
    tags=["Enrichments"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "/files/process",
    response_model=FileProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="파일 처리",
    description="Path에서 파일을 읽고 DB에 저장합니다.",
    response_description="파일 처리 결과",
)
async def process_file(
    request: Request,
    body: FileProcessRequest,
) -> FileProcessResponse:
    try:
        container: Container = request.app.state.container
        container.reader_source_key.override(body.source.value)
        company_info_writer = container.company_info_writer()

        # Process the file
        file_path = body.file_path
        result = await company_info_writer.process_file(file_path)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File processing failed: {result.message}",
            )

        return FileProcessResponse(
            message="File processed successfully",
            file_path=file_path,
            status="success",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
