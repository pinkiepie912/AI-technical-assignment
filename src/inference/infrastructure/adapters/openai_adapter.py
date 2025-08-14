from openai import AsyncOpenAI

from inference.application.ports.llm_port import LlmClientPort
from inference.domain.vos.openai_models import LLMModel


class OpenAIClient(LlmClientPort):
    """
    OpenAI API를 직접 호출하는 LLM 클라이언트 구현체
    """

    def __init__(self, api_key: str):
        """
        OpenAI 클라이언트를 초기화합니다.

        Args:
            api_key: OpenAI API 키. 제공되지 않으면 환경변수에서 가져옵니다.
        """
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or provide api_key parameter."
            )

        self.api_key = api_key

        # AsyncOpenAI 클라이언트 초기화
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def answer(self, question: str, context: str, model: LLMModel) -> str:
        """
        주어진 질문과 컨텍스트를 바탕으로 OpenAI API에 요청하여 답변을 받습니다.

        Args:
            question: 질문 내용
            context: 컨텍스트 정보
            model: 사용할 LLM 모델

        Returns:
            str: OpenAI API의 응답 텍스트

        Raises:
            Exception: API 호출 중 오류 발생 시
        """
        try:
            # 프롬프트 구성
            prompt = f"{context}\n\n{question}"

            # OpenAI Chat Completions API 호출
            response = await self.client.chat.completions.create(
                model=model.value,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 일관된 추론을 위해 낮은 temperature 사용
                max_completion_tokens=2000,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0,
            )

            # 응답에서 텍스트 추출
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                if message and message.content:
                    return message.content.strip()

            # 응답이 비어있는 경우
            return "OpenAI API로부터 유효한 응답을 받지 못했습니다."

        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}") from e
