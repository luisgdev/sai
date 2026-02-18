"""Main module."""

import asyncio
from pprint import pformat

import assets
import config
import httpx
import utils
from llm import OllamaError, OllamaHandler
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

ollama_handler = OllamaHandler(url=config.OLLAMA_URL, timeout=config.HTTP_TIMEOUT)


async def process_ollama_response(query: str, model_name: str = config.OLLAMA_MODEL) -> None:
    """Process Ollama response in real time."""
    with Live(console=console, refresh_per_second=config.CLI_REFRESH_TIME) as live:
        panel = Panel(
            renderable="",
            title="Generating ⏳",
            subtitle=model_name,
            title_align="right",
            padding=(0, 1),
            border_style="yellow",
            expand=False,
        )
        try:
            async for chunk in ollama_handler.stream_response(
                payload={"model": model_name, "prompt": query},
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
    model = config.OLLAMA_MODEL
    while query != "/quit":
        query = input("> ")
        if query == "/help":
            main_panel.renderable = Markdown(assets.HELP_MESSAGE)
            console.print(main_panel)
        elif query == "/model":
            models = asyncio.run(ollama_handler.list_models())
            model = utils.item_selection_input(
                message="Select the model to use: ",
                items=models,
            )
            console.print(f"Selected model: {model}")
        elif query == "/quit":
            console.print("Goodbye!")
        else:
            asyncio.run(process_ollama_response(query=query, model_name=model))


if __name__ == "__main__":
    main()
