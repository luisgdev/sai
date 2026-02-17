"""Main module."""

import asyncio
import json
import sys

import httpx
from rich import print
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()
OLLAMA_URL: str = "http://localhost:11434/api/generate"
OLLAMA_MODEL: str = "llama3.2:1b"


async def stream_ollama_response(url: str, payload: dict):
    """
    Sends a POST request to the Ollama API and streams the response in real time.

    Args:
        url: The Ollama API endpoint (e.g., "http://localhost:11434/api/generate")
        payload: The JSON payload to send (e.g., {"model": "llama2", "prompt": "Is the sky blue?"})
    """
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, json=payload) as response:
            # Create a Live display
            with Live(console=console, refresh_per_second=20) as live:
                md_text = ""
                async for chunk in response.aiter_text():
                    data = json.loads(chunk)
                    if "error" in data:
                        print("ERROR: " + data["error"])
                        break
                    md_text += data.get("response", "\n")

                    panel = Panel(
                        Markdown(md_text),
                        title="Sai conversation",
                        subtitle="AI response",
                        title_align="left",
                        padding=(0, 1),
                        border_style="yellow",
                        expand=True,
                    )
                    live.update(panel)


def main():
    print("Hello from chai!")
    asyncio.run(
        stream_ollama_response(
            url=OLLAMA_URL,
            payload={"model": OLLAMA_MODEL, "prompt": sys.argv[1]},
        )
    )
    print("\n")


if __name__ == "__main__":
    main()
