"""Main module."""

import asyncio
import json
import sys
from pprint import pformat
from typing import Any, AsyncGenerator

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()
OLLAMA_URL: str = "http://localhost:11434/api/generate"
OLLAMA_MODEL: str = "qwen3:1.7b"


class OllamaError(Exception):
    """Exception raised when Ollama API responded with an error."""


async def stream_ollama_response(url: str, payload: dict) -> AsyncGenerator[str, Any]:
    """Sends a POST request to the Ollama API and streams the response in real time."""
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, json=payload) as response:
            md_text = ""
            is_thinking = False
            async for chunk in response.aiter_text():
                data = json.loads(chunk)
                if "error" in data:
                    raise OllamaError(data["error"])
                if "thinking" in data:
                    if not is_thinking:
                        md_text += "THINKING: "
                        is_thinking = True
                    md_text += data["thinking"]
                else:
                    if is_thinking:
                        md_text += "\n\n---\nRESPONSE: "
                        is_thinking = False
                    md_text += data.get("response", "\n")
                yield md_text


async def process_ollama_response() -> None:
    """Process Ollama response in real time."""
    with Live(console=console, refresh_per_second=20) as live:
        panel = Panel(
            renderable="",
            title="Sai conversation",
            subtitle="AI response",
            title_align="left",
            padding=(0, 1),
            border_style="yellow",
            expand=True,
        )
        try:
            async for chunk in stream_ollama_response(
                url=OLLAMA_URL,
                payload={"model": OLLAMA_MODEL, "prompt": sys.argv[1]},
            ):
                panel.renderable = Markdown(chunk)
                live.update(panel)
        except httpx.ConnectError as error:
            console.log(pformat(error))
        except OllamaError as error:
            console.log(pformat(error))


def main():
    """Main function."""
    print("Hello from sai!")
    asyncio.run(process_ollama_response())


if __name__ == "__main__":
    main()
