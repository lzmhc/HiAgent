"""LLM适配器 - 支持OpenAI、Anthropic、Gemini等不同接口格式"""
from abc import ABC, abstractmethod
from typing import Optional, Iterator, List, Dict, Any
from openai.types.chat import ChatCompletionChunk
class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    def __init__(self, model: str, api_key: str, base_url: Optional[str], timeout: int, temperature: float, max_tokens: int):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None

    @abstractmethod
    def create_client(self) -> Any:
        """创建客户端实例"""
        pass

    @abstractmethod
    def stream_invoke(self, messages: List[Dict], tools : Optional[list] = None) -> Iterator[ChatCompletionChunk]:
        pass

class OpenAIAdapter(BaseLLMAdapter):
    def stream_invoke(self, messages: List[Dict], tools : Optional[list] = None) -> Iterator[ChatCompletionChunk]:
        if not self.client:
            self.client = self.create_client()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools,
                tool_choice="auto"
            )
            return response
        except Exception as e:
            raise Exception(f"OpenAI API流式调用失败: {str(e)}")

    def create_client(self) -> Any:
        """创建OpenAI客户端"""
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

def create_adapter(
        model: str,
        api_key: str,
        base_url: Optional[str],
        timeout: int,
        temperature: float,
        max_tokens: int
) -> BaseLLMAdapter:
    return OpenAIAdapter(model, api_key, base_url, timeout, temperature, max_tokens)
