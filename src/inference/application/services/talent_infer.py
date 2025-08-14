import calendar
import hashlib
import json
import re
from datetime import date
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from inference.application.ports.llm_port import LlmClientPort
from inference.application.templates.inference_template import (
    TalentInferencePromptTemplates,
)
from inference.controllers.dtos.talent_infer import (
    StartEndDate,
    TalentProfile,
)
from inference.domain.aggregates.talent_career_journey import TalentCareerJourney
from inference.domain.entities.news_chunk import NewsChunk
from inference.domain.repositories.company_context_search_port import (
    CompanyContextSearchPort,
    CompanySearchContextParam,
)
from inference.domain.repositories.news_search_port import (
    NewsSearchPort,
    NewsSearchQuery,
    NewsSearchRequest,
)
from inference.domain.services.position_context_aggregator import (
    PositionContextAggregator,
)
from inference.domain.vos.openai_models import LLMModel
from shared.cache.cache_port import CachePort


class TalentInference:
    def __init__(
        self,
        company_search_adapter: CompanyContextSearchPort,
        news_search_adapter: NewsSearchPort,
        llm_client: LlmClientPort,
        cache_adapter: CachePort,
    ):
        self.company_search_adapter = company_search_adapter
        self.news_search_adapter = news_search_adapter
        self.llm_client = llm_client
        self.cache_adapter = cache_adapter

    async def inference(self, talent_profile: TalentProfile):
        """
        인재 프로필에서 경력 정보를 추출하여 LLM으로 추론된 경험과 능력 태그 반환

        Args:
            talent_profile: 원본 인재 프로필 데이터

        Returns:
            dict: LLM 추론 응답 (경험/능력 태그 형태)
        """
        cache_key = self._generate_cache_key(talent_profile)

        cached_result = await self.cache_adapter.get(cache_key)
        if cached_result:
            return cached_result

        # inference 수행
        result = await self._perform_inference(talent_profile)

        # cache
        await self.cache_adapter.set(cache_key, result, ttl=60 * 60)

        return result

    async def _perform_inference(self, talent_profile: TalentProfile) -> dict:
        """
        추론 로직 수행

        Args:
            talent_profile: 원본 인재 프로필 데이터

        Returns:
            dict: LLM 추론 결과
        """
        # 1. 경력 사항에서 회사별 재직 기간 추출
        company_params = self._extract_company_params(talent_profile)

        # 2. 회사 정보 조회
        company_contexts = await self.company_search_adapter.search(company_params)

        # 3. 뉴스 검색 쿼리 생성 및 실행
        news_by_companies = await self._search_related_news(
            talent_profile, company_contexts
        )

        # 4. Position별 컨텍스트 정보 집계
        career_journey = PositionContextAggregator.aggregate_career_journey(
            talent_profile=talent_profile,
            company_contexts=company_contexts,
            news_by_companies=news_by_companies,
        )

        # 5. Position 순서 기반 구조화된 프롬프트 생성
        formatted_prompt = self._create_structured_prompt(career_journey)

        # 6. LLM API 호출하여 경험 태그 추론
        return await self._execute_llm_inference(formatted_prompt)

    def _extract_company_params(
        self, talent_profile: TalentProfile
    ) -> List[CompanySearchContextParam]:
        """
        TalentProfile에서 회사 검색 파라미터 추출

        Args:
            talent_profile: 인재 프로필

        Returns:
            List[CompanySearchContextParam]: 회사 검색용 파라미터 목록
        """
        company_params: List[CompanySearchContextParam] = []

        for position in talent_profile.positions:
            start_date, end_date = self._extract_date_range(position.startEndDate)
            company_params.append(
                CompanySearchContextParam(
                    alias=position.companyName,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        return company_params

    async def _search_related_news(
        self, talent_profile: TalentProfile, company_contexts: List
    ) -> Dict[UUID, List[NewsChunk]]:
        """
        회사 컨텍스트 정보를 바탕으로 관련 뉴스 검색

        Args:
            talent_profile: 인재 프로필
            company_contexts: 회사 컨텍스트 목록

        Returns:
            Dict[UUID, List[NewsChunk]]: 회사ID별 뉴스 목록
        """
        company_map = {
            alias.lower().strip(): ctx.company
            for ctx in company_contexts
            for alias in ctx.company.aliases
        }

        # 뉴스 검색 쿼리 생성
        queries = []
        for position in talent_profile.positions:
            company_key = position.companyName.lower().strip()
            company = company_map.get(company_key)

            if not company or not position.description:
                continue

            start_date, end_date = self._extract_date_range(position.startEndDate)
            queries.append(
                NewsSearchQuery(
                    company_id=company.id,
                    query_text=position.description,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        # 뉴스 검색 실행
        if not queries:
            return {}

        search_result = await self.news_search_adapter.search(
            NewsSearchRequest(
                queries=queries,
                limit_per_query=5,
                similarity_threshold=0.5,
            )
        )

        # 결과 매핑: 회사 ID별 뉴스 목록
        news_by_companies: Dict[UUID, List[NewsChunk]] = {}
        for news_result in search_result:
            news_by_companies[news_result.company_id] = news_result.news_chunks

        return news_by_companies

    def _create_structured_prompt(self, career_journey: TalentCareerJourney) -> str:
        """
        TalentCareerJourney를 바탕으로 Position 순서 기반 구조화된 프롬프트 생성

        Args:
            career_journey: 경력 여정 애그리게이트

        Returns:
            str: 구조화된 프롬프트
        """
        template = (
            TalentInferencePromptTemplates.get_talent_experience_inference_template()
        )

        # Position 순서 기반으로 데이터 구조화
        chronological_contexts = career_journey.get_chronological_journey()

        # 프롬프트 포맷팅 (개선된 데이터 구조 사용)
        return template.format(
            talent_profile=career_journey.talent_profile,
            career_journey=career_journey,
            chronological_contexts=chronological_contexts,
        )

    async def _execute_llm_inference(self, formatted_prompt: str) -> dict:
        """
        LLM API 호출 및 결과 처리

        Args:
            formatted_prompt: 형식화된 프롬프트

        Returns:
            dict: 추론 결과 또는 오류 매시지
        """
        inference_result = ""
        try:
            inference_result = await self.llm_client.answer(
                question="",
                context=formatted_prompt,
                model=LLMModel.GPT_4O_MINI,
            )

            # JSON 반응 파싱
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

    def _extract_date_range(
        self, date_range: StartEndDate
    ) -> Tuple[date, Optional[date]]:
        """
        StartEndDate에서 실제 date 객체로 변환

        Args:
            date_range: 시작/종료 날짜 정보

        Returns:
            Tuple[date, Optional[date]]: 시작날짜, 종료날짜
        """
        start_date = date(date_range.start.year, date_range.start.month or 1, 1)
        end_date = None

        if date_range.end and date_range.end.year and date_range.end.month:
            last_day = calendar.monthrange(date_range.end.year, date_range.end.month)[1]
            end_date = date(date_range.end.year, date_range.end.month, last_day)
        else:
            end_date = None

        return start_date, end_date

    def _generate_cache_key(self, talent_profile: TalentProfile) -> str:
        """
        TalentProfile을 기반으로 캐시 키 생성

        Args:
            talent_profile: 인재 프로필

        Returns:
            str: 생성된 캐시 키
        """

        position_data = []

        for position in talent_profile.positions:
            normalized_date = {
                "start": {
                    "year": position.startEndDate.start.year,
                    "month": position.startEndDate.start.month,
                },
                "end": (
                    {
                        "year": position.startEndDate.end.year,
                        "month": position.startEndDate.end.month,
                    }
                    if position.startEndDate.end
                    else None
                ),
            }

            position_data.append(
                {
                    "companyName": position.companyName.strip().lower(),
                    "title": position.title.strip().lower(),
                    "description": position.description.strip().lower(),
                    "startEndDate": normalized_date,
                }
            )

        # Position 데이터를 시작일 기준으로 정렬하여 일관성 보장
        position_data.sort(
            key=lambda p: (
                p["startEndDate"]["start"]["year"],
                p["startEndDate"]["start"]["month"] or 1,
            )
        )

        position_json = json.dumps(position_data, ensure_ascii=False, sort_keys=True)
        hash_object = hashlib.sha256(position_json.encode("utf-8"))

        return f"talent_inference:{hash_object.hexdigest()}"
