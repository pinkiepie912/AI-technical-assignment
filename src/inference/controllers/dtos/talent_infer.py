from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

__all__ = [
    "TalentProfile",
]


class DateModel(BaseModel):
    year: int = Field(..., description="연도")
    month: Optional[int] = Field(None, description="월 (1-12)")

    model_config = ConfigDict(frozen=True)


class StartEndDate(BaseModel):
    start: DateModel = Field(..., description="시작 날짜")
    end: Optional[DateModel] = Field(None, description="종료 날짜")

    model_config = ConfigDict(frozen=True)


class OriginStartEndDate(BaseModel):
    startDateOn: DateModel = Field(..., description="시작 날짜")
    endDateOn: DateModel = Field(..., description="종료 날짜")

    model_config = ConfigDict(frozen=True)


class Education(BaseModel):
    degreeName: str = Field(..., description="학위명")
    fieldOfStudy: str = Field(..., description="전공 분야")
    schoolName: str = Field(..., description="학교명")
    startEndDate: str = Field(..., description="재학 기간 (문자열 형태)")
    description: str = Field(..., description="교육 설명")
    grade: str = Field(..., description="성적")
    originStartEndDate: OriginStartEndDate = Field(..., description="원본 날짜 정보")

    model_config = ConfigDict(frozen=True)


class Position(BaseModel):
    companyName: str = Field(..., description="회사명")
    title: str = Field(..., description="직책")
    companyLocation: str = Field(..., description="회사 위치")
    description: str = Field(..., description="업무 설명")
    companyLogo: str = Field(..., description="회사 로고 URL")
    startEndDate: StartEndDate = Field(..., description="재직 기간")

    model_config = ConfigDict(frozen=True)


class TalentProfile(BaseModel):
    firstName: str = Field(..., description="이름")
    lastName: str = Field(..., description="성")
    headline: str = Field(..., description="헤드라인")
    summary: str = Field(..., description="자기소개/요약")
    photoUrl: str = Field(..., description="프로필 사진 URL")
    linkedinUrl: HttpUrl = Field(..., description="링크드인 URL")
    industryName: str = Field(..., description="업계명")

    skills: List[str] = Field(default_factory=list, description="보유 스킬 목록")
    positions: List[Position] = Field(default_factory=list, description="경력 사항")
    educations: List[Education] = Field(default_factory=list, description="교육 사항")

    website: List[str] = Field(default_factory=list, description="웹사이트 목록")
    projects: List[str] = Field(default_factory=list, description="프로젝트 목록")
    recommendations: List[str] = Field(default_factory=list, description="추천서 목록")
