"""Main module."""

import asyncio
from pprint import pformat

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from app import assets, config, repository, utils
from app.llm import OllamaError, OllamaHandler

console = Console()
ollama_settings = repository.get_ollama_settings()
ollama_handler = OllamaHandler(url=ollama_settings.base_url, timeout=config.HTTP_TIMEOUT)


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
            return str(panel.renderable.markup)
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
        if query == "/setup":
            console.print("Setup Ollama")
            ollama_url = utils.text_input("Enter Ollama URL")
            ollama_settings.base_url = ollama_url
            ollama_settings.save()
            ollama_handler.base_url = ollama_url
            console.print(f"Ollama URL set: {ollama_settings.base_url}")
        elif query == "/help":
            main_panel.renderable = Markdown(assets.HELP_MESSAGE)
            console.print(main_panel)
        elif query == "/model":
            try:
                models = asyncio.run(ollama_handler.list_models())
                model = utils.item_selection_input(
                    message="Select the model to use",
                    items=models,
                )
                console.print(f"Selected model: {model}")
                ollama_settings.model_name = model
                ollama_settings.save()
            except (httpx.ConnectError, httpx.UnsupportedProtocol) as error:
                console.log(pformat(error))
                console.print("Tip: Make sure Ollama is running and run `/setup` to set the URL.")
        elif query == "/quit":
            console.print("Goodbye! :wave:")
        else:
            messages.append({"role": "user", "content": query})
            response = asyncio.run(process_ollama_response(messages=messages, model_name=model))
            messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
