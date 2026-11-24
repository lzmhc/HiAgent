from abc import ABC, abstractmethod
from typing import Optional, Iterator, List, Any, Dict
from openai.types.chat import ChatCompletionChunk
class BaseLLMAdapter(ABC):
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
        pass

    @abstractmethod
    def stream_invoke(self, messages: List[Dict], tools : List[Dict]) -> Iterator[ChatCompletionChunk]:
        pass

class OpenAIAdapter(BaseLLMAdapter):
    def create_client(self) -> Any:
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    def stream_invoke(self, messages: List[Dict], tools: List[Dict]) -> Iterator[ChatCompletionChunk]:
        if not self.client:
            self.client = self.create_client()
        try:
            response = self.client.responses.create(
                model=self.model,
                input=messages,
                stream=True,
                temperature=self.temperature,
                tools=tools,
                reasoning={"effort": "low"},
            )
            return response
        except Exception as e:
            raise Exception(f"Error response: {str(e)}")

def create_adapter(
        model: str,
        api_key: str,
        base_url: Optional[str],
        timeout: int,
        temperature: float,
        max_tokens: int
) -> BaseLLMAdapter:
    return OpenAIAdapter(model, api_key, base_url, timeout, temperature, max_tokens)
