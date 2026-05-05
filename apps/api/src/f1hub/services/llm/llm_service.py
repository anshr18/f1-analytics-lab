"""
LLM Service

Google Gemini client wrapper for chat completions and text generation.
"""

from typing import List, Dict, Any, Optional
import google.generativeai as genai
from f1hub.core.config import settings


class LLMService:
    """Service for interacting with Google Gemini for chat completions."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE

    def _build_model(self, model_name: str, system_instruction: Optional[str]) -> genai.GenerativeModel:
        kwargs: Dict[str, Any] = {}
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        return genai.GenerativeModel(model_name, **kwargs)

    def _convert_messages(self, messages: List[Dict[str, str]]):
        """Convert OpenAI-style messages to Gemini format, extracting system prompt."""
        system_instruction = None
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                system_instruction = content
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})
        return system_instruction, gemini_messages

    def _gen_config(self, temperature: Optional[float], max_tokens: Optional[int]) -> genai.types.GenerationConfig:
        return genai.types.GenerationConfig(
            max_output_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
        )

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        m = self._build_model(model or self.model, None)
        result = m.count_tokens(text)
        return result.total_tokens

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        model_name = model or self.model
        system_instruction, gemini_messages = self._convert_messages(messages)
        m = self._build_model(model_name, system_instruction)
        response = m.generate_content(gemini_messages, generation_config=self._gen_config(temperature, max_tokens))

        return {
            "content": response.text,
            "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "STOP",
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            },
            "model": model_name,
        }

    async def generate_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        model_name = model or self.model
        system_instruction, gemini_messages = self._convert_messages(messages)
        m = self._build_model(model_name, system_instruction)
        response = await m.generate_content_async(
            gemini_messages, generation_config=self._gen_config(temperature, max_tokens)
        )

        return {
            "content": response.text,
            "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "STOP",
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            },
            "model": model_name,
        }

    def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ):
        model_name = model or self.model
        system_instruction, gemini_messages = self._convert_messages(messages)
        m = self._build_model(model_name, system_instruction)
        response = m.generate_content(
            gemini_messages, generation_config=self._gen_config(temperature, max_tokens), stream=True
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def generate_streaming_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ):
        model_name = model or self.model
        system_instruction, gemini_messages = self._convert_messages(messages)
        m = self._build_model(model_name, system_instruction)
        response = await m.generate_content_async(
            gemini_messages, generation_config=self._gen_config(temperature, max_tokens), stream=True
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text
