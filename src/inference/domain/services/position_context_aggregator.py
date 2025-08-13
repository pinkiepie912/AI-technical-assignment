from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from inference.controllers.dtos.talent_infer import Position, TalentProfile
from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.aggregates.talent_career_journey import TalentCareerJourney
from inference.domain.entities.news_chunk import NewsChunk
from inference.domain.vos.position_with_context import PositionWithContext

__all__ = ["PositionContextAggregator"]


class PositionContextAggregator:
    """
    Position과 관련 컨텍스트 정보를 집계하는 Domain Service

    DDD의 Domain Service 패턴을 적용하여 복잡한 비즈니스 로직을 처리합니다.
    여러 Repository와 외부 서비스에서 가져온 데이터를 결합하여
    일관성 있는 도메인 객체를 생성합니다.
    """

    @staticmethod
    def aggregate_career_journey(
        talent_profile: TalentProfile,
        company_contexts: List[CompanyContext],
        news_by_companies: Dict[UUID, List[NewsChunk]],
    ) -> TalentCareerJourney:
        """
        인재 프로필과 외부 컨텍스트 정보를 결합하여 TalentCareerJourney 생성

        Args:
            talent_profile: 인재 기본 프로필 정보
            company_contexts: 회사별 컨텍스트 정보 목록
            news_by_companies: 회사ID별 뉴스 목록 매핑

        Returns:
            TalentCareerJourney: 완성된 경력 여정 Aggregate
        """
        company_context_map = PositionContextAggregator._build_company_context_map(
            company_contexts
        )

        # Position별 컨텍스트 정보 집계
        position_contexts: List[PositionWithContext] = []

        for position in talent_profile.positions:
            # 회사명으로 CompanyContext 검색
            company_context = PositionContextAggregator._find_company_context(
                position, company_context_map
            )

            # 관련 뉴스 검색
            related_news = PositionContextAggregator._find_related_news(
                company_context, news_by_companies
            )

            # PositionWithContext 생성
            position_with_context = PositionWithContext(
                position=position,
                company_context=company_context,
                related_news=related_news,
            )

            position_contexts.append(position_with_context)

        return TalentCareerJourney(
            talent_profile=talent_profile, position_contexts=position_contexts
        )

    @staticmethod
    def _build_company_context_map(
        company_contexts: List[CompanyContext],
    ) -> Dict[str, CompanyContext]:
        """
        회사 별명(alias)을 키로 하는 CompanyContext 매핑 테이블 생성

        성능 최적화: 중첩 루프 대신 평면화된 매핑 구조 사용

        Args:
            company_contexts: 회사 컨텍스트 목록

        Returns:
            Dict[str, CompanyContext]: 회사 별명을 키로 하는 매핑 테이블
        """
        company_map: Dict[str, CompanyContext] = {}

        for context in company_contexts:
            # 회사의 모든 별명에 대해 매핑 생성
            for alias in context.company.aliases:
                company_map[alias.lower().strip()] = context

        return company_map

    @staticmethod
    def _find_company_context(
        position: Position, company_context_map: Dict[str, CompanyContext]
    ) -> Optional[CompanyContext]:
        """
        Position의 회사명으로 해당하는 CompanyContext 검색

        대소문자 무시, 공백 제거하여 유연한 매칭 수행

        Args:
            position: 검색할 Position 정보
            company_context_map: 회사 컨텍스트 매핑 테이블

        Returns:
            Optional[CompanyContext]: 찾은 회사 컨텍스트, 없으면 None
        """
        company_key = position.companyName.lower().strip()
        return company_context_map.get(company_key)

    @staticmethod
    def _find_related_news(
        company_context: Optional[CompanyContext],
        news_by_companies: Dict[UUID, List[NewsChunk]],
    ) -> List[NewsChunk]:
        """
        Position과 연관된 뉴스 검색

        Args:
            position: 검색 기준이 되는 Position
            company_context: 회사 컨텍스트 정보 (없을 수 있음)
            news_by_companies: 회사ID별 뉴스 매핑

        Returns:
            List[NewsChunk]: 관련 뉴스 목록 (빈 목록일 수 있음)
        """
        if not company_context:
            return []

        company_id = company_context.company.id
        return news_by_companies.get(company_id, [])

