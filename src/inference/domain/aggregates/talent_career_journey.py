from __future__ import annotations

from dataclasses import dataclass
from typing import List

from inference.controllers.dtos.talent_infer import TalentProfile
from inference.domain.vos.position_with_context import PositionWithContext

__all__ = ["TalentCareerJourney"]


@dataclass
class TalentCareerJourney:
    """
    인재의 경력 여정을 나타내는 Aggregate Root
    """

    talent_profile: TalentProfile
    position_contexts: List[PositionWithContext]

    def get_chronological_journey(self) -> List[PositionWithContext]:
        """
        시간순 정렬된 경력 여정 반환

        경력 시작일 기준으로 오름차순 정렬하여,
        시간의 흐름에 따른 경력 발전 과정을 명확히 보여줍니다.

        Returns:
            List[PositionWithContext]: 시간순으로 정렬된 경력 컨텍스트 목록
        """
        return sorted(
            self.position_contexts, key=lambda ctx: ctx.get_chronological_order_key()
        )

