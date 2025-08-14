from typing import List

from pydantic import BaseModel, Field


class TalentInferRes(BaseModel):
    tag: str = Field(
        ..., description="인재 추론 결과 태그", examples=["성장기스타트업 경험"]
    )
    inference: str = Field(
        ...,
        description="인재 추론 결과 설명",
        examples=["성장기 스타트업에서의 경험을 보유한 인재입니다."],
    )


class TalentInferResponse(BaseModel):
    experience_tags: list[str] = Field(
        ...,
        description="추론된 경험 태그 리스트",
        examples=['["성장기스타트업 경험", "대규모 회사 경험", "리더십"]'],
    )
    competency_tags: list[str] = Field(
        ...,
        description="추론된 역량 태그 리스트",
        examples=['["전략 기획", "재무 관리", "조직 관리"]'],
    )
    inferences: List[TalentInferRes]
