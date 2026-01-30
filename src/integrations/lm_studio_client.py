"""
LM Studio Client - OpenAI-compatible client for remote LM Studio server.
Handles connection, health checks, and error recovery.
"""
import time
from typing import Any, Generator

from openai import OpenAI
from openai import APIConnectionError, APITimeoutError

from src.config import settings


class LMStudioClient:
    """
    Client for remote LM Studio server.
    Uses OpenAI SDK with custom base URL.
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        api_key: str | None = None
    ):
        """
        Initialize LM Studio client.
        
        Args:
            base_url: LM Studio server URL. Defaults to config.
            model: Model name. Defaults to config.
            timeout: Request timeout in seconds. Defaults to config.
            api_key: API key for LM Studio server. Defaults to config.
        """
        config = settings()["lm_studio"]
        
        self.base_url = base_url or config["base_url"]
        self.model = model or config["model"]
        self.timeout = timeout or config["timeout"]
        self.api_key = api_key or config.get("api_key", "not-needed")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )
    
    def health_check(self) -> dict[str, Any]:
        """
        Check if LM Studio server is running and responsive.
        
        Returns:
            Dict with status and details.
        """
        try:
            # Try to list models
            models = self.client.models.list()
            model_names = [m.id for m in models.data]
            
            return {
                "status": "healthy",
                "server_url": self.base_url,
                "available_models": model_names,
                "configured_model": self.model,
                "model_available": self.model in model_names,
            }
        except APIConnectionError as e:
            return {
                "status": "error",
                "error": "Cannot connect to LM Studio server",
                "details": str(e),
                "server_url": self.base_url,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(type(e).__name__),
                "details": str(e),
                "server_url": self.base_url,
            }
    
    def is_available(self) -> bool:
        """Quick check if server is available."""
        health = self.health_check()
        return health["status"] == "healthy"
    
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: User prompt.
            system_prompt: Optional system message.
            temperature: Override temperature.
            max_tokens: Override max tokens.
        
        Returns:
            Generated text.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content
        
        except APIConnectionError:
            raise ConnectionError(
                f"Cannot connect to LM Studio server at {self.base_url}. "
                "Please ensure LM Studio is running and the server is accessible."
            )
        except APITimeoutError:
            raise TimeoutError(
                f"Request to LM Studio server timed out after {self.timeout}s. "
                "The model may be loading or the request may be too large."
            )
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Generator[str, None, None]:
        """
        Stream text generation.
        
        Args:
            prompt: User prompt.
            system_prompt: Optional system message.
            temperature: Override temperature.
            max_tokens: Override max tokens.
        
        Yields:
            Text chunks as they're generated.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except APIConnectionError:
            raise ConnectionError(
                f"Cannot connect to LM Studio server at {self.base_url}. "
                "Please ensure LM Studio is running and the server is accessible."
            )


# Global client instance (lazy loaded)
_client: LMStudioClient | None = None


def get_lm_studio_client(model: str | None = None) -> LMStudioClient:
    """Get LM Studio client instance. Creates new instance if model is specified."""
    global _client
    if model is not None:
        # Create new client with specified model
        return LMStudioClient(model=model)
    if _client is None:
        _client = LMStudioClient()
    return _client


def check_lm_studio_server() -> dict[str, Any]:
    """Quick health check function."""
    client = get_lm_studio_client()
    return client.health_check()


# Legacy aliases for backward compatibility
get_jan_client = get_lm_studio_client
check_jan_server = check_lm_studio_server


if __name__ == "__main__":
    # Quick test
    print("Checking LM Studio server connection...")
    status = check_lm_studio_server()
    
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if status["status"] == "healthy":
        print("\nTesting generation...")
        client = get_lm_studio_client()
        response = client.generate("Say hello in one sentence.")
        print(f"Response: {response}")
