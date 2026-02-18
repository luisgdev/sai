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


async def process_ollama_response(
    messages: list[dict[str, str]], model_name: str = config.OLLAMA_MODEL
) -> str | None:
    """Process Ollama response in real time."""
    with Live(console=console, refresh_per_second=config.CLI_REFRESH_TIME) as live:
        panel = Panel(
            renderable="",
            title="Generating :hourglass_flowing_sand:",
            subtitle=model_name,
            title_align="right",
            padding=(0, 1),
            border_style="yellow",
            expand=False,
        )
        try:
            async for chunk in ollama_handler.stream_response(
                payload={"model": model_name, "messages": messages},
            ):
                panel.renderable = Markdown(chunk)
                live.update(panel)
            panel.title = "LLM Response :heavy_check_mark:"
            live.update(panel)
            return panel.renderable.markup
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
    messages: list[dict[str, str]] = [{"role": "system", "content": assets.DEFAULT_PROMPT}]
    query: str = ""
    model = config.OLLAMA_MODEL
    console.print(main_panel)
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
            console.print("Goodbye! :wave:")
        else:
            messages.append({"role": "user", "content": query})
            response = asyncio.run(process_ollama_response(messages=messages, model_name=model))
            messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
