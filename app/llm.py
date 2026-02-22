"""LLM module"""

import json
from typing import Any, AsyncGenerator

import httpx


class OllamaError(Exception):
    """Exception raised when Ollama API responded with an error."""


class OllamaHandler:
    """Handler for interacting with the Ollama API."""

    def __init__(self, url: str, timeout: int) -> None:
        self.base_url = url
        self.timeout = timeout

    async def list_models(self) -> list[str]:
        """List OLLAMA models"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            result = await client.get(url=f"{self.base_url}/api/tags")
            models = [item["model"] for item in result.json()["models"]]
            return models

    async def preload_model(self, model: str) -> bool:
        """Preload a model into Ollama to get faster response times"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            result = await client.post(url=f"{self.base_url}/api/chat", params={"model": model})
            return result.json().get("done")

    async def stream_response(self, payload: dict[str, Any]) -> AsyncGenerator[str, Any]:
        """Sends a POST request to the Ollama API and streams the response in real time."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as response:
                md_text = ""
                is_thinking = False
                async for chunk in response.aiter_text():
                    data = json.loads(chunk)
                    if "error" in data:
                        raise OllamaError(data["error"])
                    if not "message" in data:
                        raise OllamaError(f"No message in response: {chunk}")
                    if "thinking" in data["message"]:
                        if not is_thinking:
                            md_text += "THINKING 🤔: "
                            is_thinking = True
                        md_text += data["message"]["thinking"]
                    else:
                        if is_thinking:
                            md_text += "\n\n---\n"
                            is_thinking = False
                        md_text += data["message"].get("content", "\n")
                    yield md_text
