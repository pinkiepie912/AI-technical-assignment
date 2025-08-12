from typing import Awaitable, Protocol

from inference.domain.vos.openai_models import LLMModel


class LlmClient(Protocol):
    def answer(
        self, question: str, context: str, model: LLMModel
    ) -> Awaitable[str]: ...
