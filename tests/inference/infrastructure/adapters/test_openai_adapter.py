import pytest
from unittest.mock import AsyncMock, MagicMock

from inference.application.ports.llm_port import LlmClientPort
from inference.infrastructure.adapters.openai_adapter import OpenAIClient
from inference.domain.vos.openai_models import LLMModel


class TestOpenAIClient:
    @pytest.fixture
    def mock_async_openai_instance(self):
        mock_create = AsyncMock()
        mock_completions = MagicMock(create=mock_create)
        mock_chat = MagicMock(completions=mock_completions)
        mock_client = MagicMock(chat=mock_chat)
        return mock_client

    @pytest.fixture
    def openai_client(self, mock_async_openai_instance):
        # Patch AsyncOpenAI to return our mock
        with pytest.MonkeyPatch().context() as m:
            m.setattr("inference.infrastructure.adapters.openai_adapter.AsyncOpenAI", MagicMock(return_value=mock_async_openai_instance))
            client = OpenAIClient(api_key="test_api_key")
            return client

    def test_init_with_api_key(self, mock_async_openai_instance):
        with pytest.MonkeyPatch().context() as m:
            m.setattr("inference.infrastructure.adapters.openai_adapter.AsyncOpenAI", mock_async_openai_instance)
            client = OpenAIClient(api_key="test_api_key")
            assert client.api_key == "test_api_key"
            mock_async_openai_instance.assert_called_once_with(api_key="test_api_key")

    def test_init_without_api_key_raises_error(self):
        with pytest.raises(ValueError, match="OpenAI API key is required"): # type: ignore
            OpenAIClient(api_key="")

    @pytest.mark.asyncio
    async def test_answer_success(self, openai_client, mock_async_openai_instance):
        # Arrange
        question = "What is the capital of France?"
        context = "Paris is the capital of France."
        model = LLMModel.GPT_4O_MINI

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "The capital of France is Paris."
        mock_async_openai_instance.chat.completions.create.return_value = mock_response

        # Act
        response_text = await openai_client.answer(question, context, model)

        # Assert
        expected_prompt = f"{context}\n\n{question}"
        mock_async_openai_instance.chat.completions.create.assert_called_once_with(
            model=model.value,
            messages=[{"role": "user", "content": expected_prompt}],
            temperature=0.1,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0,
        )
        assert response_text == "The capital of France is Paris."

    @pytest.mark.asyncio
    async def test_answer_empty_response_choices(self, openai_client, mock_async_openai_instance):
        # Arrange
        question = "Test question"
        context = "Test context"
        model = LLMModel.GPT_4O_MINI

        mock_response = MagicMock()
        mock_response.choices = []
        mock_async_openai_instance.chat.completions.create.return_value = mock_response

        # Act
        response_text = await openai_client.answer(question, context, model)

        # Assert
        assert response_text == "OpenAI API로부터 유효한 응답을 받지 못했습니다."

    @pytest.mark.asyncio
    async def test_answer_empty_message_content(self, openai_client, mock_async_openai_instance):
        # Arrange
        question = "Test question"
        context = "Test context"
        model = LLMModel.GPT_4O_MINI

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = None
        mock_async_openai_instance.chat.completions.create.return_value = mock_response

        # Act
        response_text = await openai_client.answer(question, context, model)

        # Assert
        assert response_text == "OpenAI API로부터 유효한 응답을 받지 못했습니다."

    @pytest.mark.asyncio
    async def test_answer_api_error_handling(self, openai_client, mock_async_openai_instance):
        # Arrange
        question = "Test question"
        context = "Test context"
        model = LLMModel.GPT_4O_MINI

        mock_async_openai_instance.chat.completions.create.side_effect = Exception("API call failed")

        # Act & Assert
        with pytest.raises(Exception, match="OpenAI API 호출 중 오류 발생: API call failed"): # type: ignore
            await openai_client.answer(question, context, model)
