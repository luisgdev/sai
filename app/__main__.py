"""Main module."""

import asyncio
import json
from pprint import pformat
from typing import Any, AsyncGenerator

import config
import assets
import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


class OllamaError(Exception):
    """Exception raised when Ollama API responded with an error."""


async def stream_ollama_response(url: str, payload: dict) -> AsyncGenerator[str, Any]:
    """Sends a POST request to the Ollama API and streams the response in real time."""
    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as client:
        async with client.stream("POST", f"{url}/api/generate", json=payload) as response:
            md_text = ""
            is_thinking = False
            async for chunk in response.aiter_text():
                data = json.loads(chunk)
                if "error" in data:
                    raise OllamaError(data["error"])
                if "thinking" in data:
                    if not is_thinking:
                        md_text += "THINKING 🧠: "
                        is_thinking = True
                    md_text += data["thinking"]
                else:
                    if is_thinking:
                        md_text += "\n\n---\n"
                        is_thinking = False
                    md_text += data.get("response", "\n")
                yield md_text


async def process_ollama_response(query: str) -> None:
    """Process Ollama response in real time."""
    with Live(console=console, refresh_per_second=config.CLI_REFRESH_TIME) as live:
        panel = Panel(
            renderable="",
            title="Generating ⏳",
            subtitle=config.OLLAMA_MODEL,
            title_align="right",
            padding=(0, 1),
            border_style="yellow",
            expand=False,
        )
        try:
            async for chunk in stream_ollama_response(
                url=config.OLLAMA_URL,
                payload={"model": config.OLLAMA_MODEL, "prompt": query},
            ):
                panel.renderable = Markdown(chunk)
                live.update(panel)
            panel.title = "LLM Response ✔️"
            live.update(panel)
        except httpx.ConnectError as error:
            console.log(pformat(error))
        except OllamaError as error:
            console.log(pformat(error))


def main():
    """Main function."""
    main_panel = Panel(
        renderable=Markdown(assets.WELCOME_MESSAGE + assets.HELP_MESSAGE),
        padding=(0, 1),
        border_style="blue",
        expand=False,
    )
    console.print(main_panel)
    query = ""
    while query != "/quit":
        query = input("> ")
        if query == "/help":
            main_panel.renderable = Markdown(assets.HELP_MESSAGE)
            console.print(main_panel)
            continue
        if query == "/quit":
            console.print("Goodbye!")
        else:
            asyncio.run(process_ollama_response(query=query))


if __name__ == "__main__":
    main()
