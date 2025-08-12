import json

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from containers import Container
from inference.application.services.talent_infer import TalentInference
from inference.controllers.dtos.talent_infer import TalentProfile

router = APIRouter(
    prefix="/api/v1/inferences",
    tags=["Inferences"],
)


@router.post(
    "/talent_infer",
    # response_model=list[CompanyAggregate],
    # status_code=status.HTTP_200_OK,
    # summary="Talent Profile Inference (Test)",
    # description="테스트용: JSON 파일의 인재 정보를 받아서 CompanyAggregate 리스트를 반환합니다.",
)
@inject
async def talent_inference(
    file: UploadFile = File(..., description="인재 정보가 담긴 JSON 파일"),
    talent_inference_service: TalentInference = Depends(
        Provide[Container.talent_inference_service]
    ),
):
    """
    인재 정보 추론 API

    Args:
        file: JSON 형태의 인재 정보 파일 (positions, educations, skills 등 포함)

    Returns:
        list[CompanyAggregate]: 인재의 경력과 매칭되는 회사 정보 리스트

    Raises:
        HTTPException: 추론 과정에서 오류가 발생한 경우
    """
    try:
        # 파일 확장자 검증
        if not file.filename.lower().endswith(".json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일은 JSON 형식이어야 합니다 (.json)",
            )

        # 파일 내용 읽기
        file_content = await file.read()

        # JSON 파싱
        try:
            talent_data = json.loads(file_content.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 JSON 형식: {str(e)}",
            )
        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일 인코딩 오류 (UTF-8 필요): {str(e)}",
            )

        # JSON 데이터를 TalentProfile로 파싱 및 검증
        raw_profile = TalentProfile.model_validate(talent_data)

        # 테스트용: CompanyAggregate 리스트 반환
        inference = await talent_inference_service.inference(raw_profile)

        return inference

    except HTTPException:
        # 이미 처리된 HTTP 예외는 다시 발생시킴
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid talent data format: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}",
        )
