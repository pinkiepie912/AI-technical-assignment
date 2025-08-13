import calendar
import json
import re
from datetime import date
from typing import List

from inference.application.ports.llm_port import LlmClientPort
from inference.application.templates.inference_template import (
    TalentInferencePromptTemplates,
)
from inference.controllers.dtos.talent_infer import (
    Position,
    TalentProfile,
)
from inference.domain.ports.company_context_search_port import (
    CompanyContextSearchPort,
    CompanySearchContextParam,
)
from inference.domain.vos.openai_models import LLMModel


class TalentInference:
    def __init__(
        self,
        company_context_search: CompanyContextSearchPort,
        llm_client: LlmClientPort,
    ):
        self.company_context_search = company_context_search
        self.llm_client = llm_client

    async def inference(self, talent_profile: TalentProfile):
        """
        인재 프로필에서 경력 정보를 추출하여 LLM으로 추론된 경험과 능력 태그 반환

        Args:
            talent_profile: 원본 인재 프로필 데이터

        Returns:
            str: LLM 추론 응답 (경험/능력 태그 형태)
        """
        # 1. 경력 사항에서 회사별 재직 기간 추출
        company_params: List[CompanySearchContextParam] = []
        for position in talent_profile.positions:
            company_params.append(self._extract_company_params(position))

        # 2. 회사 정보 조회
        company_contexts = await self.company_context_search.search(company_params)

        # 4. RichPromptTemplate을 사용하여 컨텍스트 생성
        template = (
            TalentInferencePromptTemplates.get_talent_experience_inference_template()
        )

        # 프롬프트 포맷팅 (Jinja2 템플릿에 객체 직접 전달)
        formatted_prompt = template.format(
            talent_profile=talent_profile, company_summaries=company_contexts
        )

        # 5. LLM API 호출하여 경험 태그 추론
        inference_result = ""
        try:
            inference_result = await self.llm_client.answer(
                question="",
                context=formatted_prompt,
                model=LLMModel.GPT_4O_MINI,
            )
            match = re.search(r"```json\s*(.*?)\s*```", inference_result, re.DOTALL)
            if not match:
                raise ValueError("JSON 파싱에 실패했습니다.")
            json_content = match.group(1)
            inference = json.loads(json_content)

            return inference

        except ValueError as e:
            return {
                "inference_result": f"LLM 응답에서 JSON 형식이 올바르지 않습니다.\ninference_result: {inference_result}",
                "error": str(e),
            }
        except Exception as e:
            return {"inference_result": "추론을 실패했습니다.", "error": str(e)}

    def _extract_company_params(self, position: Position) -> CompanySearchContextParam:
        # 재직 기간 추출

        date_range = position.startEndDate
        start_date = date(date_range.start.year, date_range.start.month or 1, 1)
        end_date = None

        if date_range.end and date_range.end.year and date_range.end.month:
            last_day = calendar.monthrange(date_range.end.year, date_range.end.month)[1]
            end_date = date(date_range.end.year, date_range.end.month, last_day)
        else:
            end_date = None

        return CompanySearchContextParam(
            alias=position.companyName,
            start_date=start_date,
            end_date=end_date,
        )
