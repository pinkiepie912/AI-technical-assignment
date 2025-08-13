from pydantic import BaseModel, Field


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
    inferences: dict[str, str] = Field(
        ...,
        description="추론된 인재 정보",
        examples=[
            {
                "상위권대학교": "서울대학교 산업공학 전공",
                "대규모회사경험": "KT에서 12년 이상 재직하며 대규모 통신사 환경에서 다양한 전략 및 기획 업무를 수행",
                "IPO경험": "밀리의서재 CFO로 재직하며 KOSDAQ 상장을 성공적으로 이끌어냄",
                "리더십경험": "밀리의서재에서 CFO로서 여러 부서를 통합 관리하며 조직의 목표 달성을 이끌어냄",
                "신규투자유치경험": "밀리의서재에서 IPO를 통해 34,500,000,000원의 투자 유치",
                "성장기스타트업경험": "밀리의서재에서 전자책 정기구독 플랫폼을 운영하며 회사의 매출을 96% 성장시킴",
            }
        ],
    )
