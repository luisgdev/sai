"""Main module."""

import asyncio
from pprint import pformat

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from app import assets, config, utils
from app.llm import OllamaError, OllamaHandler
from app.roles import RolesManager

console = Console()


class ChatSession:
    """Manages a chat session with configuration, handler, and message history."""

    def __init__(self) -> None:
        self.cfg = config.OllamaConfig.load()
        self.handler = OllamaHandler(url=self.cfg.base_url, timeout=config.HTTP_TIMEOUT)
        self.roles_manager = RolesManager()
        role = self.roles_manager.get_by_name(self.cfg.role) or self.roles_manager.get_default()
        self.messages: list[dict[str, str]] = [{"role": "system", "content": role.prompt}]

    def _refresh_handler(self) -> None:
        """Recreate handler with current config."""
        self.handler = OllamaHandler(url=self.cfg.base_url, timeout=config.HTTP_TIMEOUT)

    def _preload_current_model(self) -> None:
        """Validate and preload current model with visual feedback."""
        with console.status("[bold blue]Checking model availability...[/bold blue]"):
            try:
                models = asyncio.run(self.handler.list_models())
                if self.cfg.model not in models:
                    console.print(f"[yellow]Model '{self.cfg.model}' not found in Ollama.[/yellow]")
                    self.select_model()
                    return
            except (httpx.ConnectError, httpx.UnsupportedProtocol):
                console.print("[yellow]Could not check models - is Ollama running?[/yellow]")
                return

        with console.status(f"[bold blue]Loading model {self.cfg.model}...[/bold blue]"):
            try:
                asyncio.run(self.handler.preload_model(self.cfg.model))
                console.print(f"[green]Model {self.cfg.model} ready![/green]")
            except (httpx.ConnectError, httpx.UnsupportedProtocol):
                console.print("[yellow]Could not preload model - is Ollama running?[/yellow]")

    def select_model(self) -> None:
        """Select model to use."""
        try:
            models = asyncio.run(self.handler.list_models())
            model = utils.item_selection_input(
                message="Select the model to use",
                items=models,
            )
            self.cfg.model = model
            self.cfg.save()
            self._preload_current_model()
        except (httpx.ConnectError, httpx.UnsupportedProtocol) as error:
            console.log(pformat(error))
            console.print("Tip: Make sure Ollama is running and run `/setup` to set the URL.")
        except KeyboardInterrupt:
            pass

    def setup(self) -> None:
        """Run user preferences setup."""
        console.print("Enter new parameters. Leave empty to use current settings")
        try:
            new_url = utils.text_input("Enter Ollama URL")
            if new_url:
                self.cfg.base_url = new_url
                self._refresh_handler()
            self.select_model()
            self.cfg.save()
            if new_url:
                console.print("Your settings have been saved!")
        except KeyboardInterrupt:
            pass

    def select_role(self) -> None:
        """Select a role to use."""
        try:
            role_name = utils.item_selection_input(
                message="Select a role",
                items=self.roles_manager.list_names(),
            )
            role = self.roles_manager.get_by_name(role_name)
            if role:
                self.cfg.role = role.name
                self.messages[0] = {"role": "system", "content": role.prompt}
                self.cfg.save()
                console.print(f"Role switched to: **{role.name}**")
        except KeyboardInterrupt:
            pass

    def add_role(self) -> None:
        """Add a new custom role."""
        try:
            name = utils.text_input("Enter role name")
            if not name:
                return
            prompt = utils.text_input("Enter role prompt")
            if not prompt:
                return
            self.roles_manager.add(name=name, prompt=prompt)
            console.print(f"Role '{name}' created successfully!")
        except ValueError as error:
            console.print(f"[red]Error:[/red] {error}")
        except KeyboardInterrupt:
            pass

    def delete_role(self) -> None:
        """Delete a custom role."""
        try:
            custom_names = [r.name for r in self.roles_manager.roles if not r.is_predefined]
            if not custom_names:
                console.print("No custom roles to delete.")
                return
            name = utils.item_selection_input(
                message="Select role to delete",
                items=custom_names,
            )
            self.roles_manager.delete(name)
            console.print(f"Role '{name}' deleted successfully!")
        except ValueError as error:
            console.print(f"[red]Error:[/red] {error}")
        except KeyboardInterrupt:
            pass

    async def _process_response(self) -> str | None:
        """Process Ollama response in real time."""
        spinner = Spinner("dots", text="Waiting for response...")
        panel: Panel | None = None
        with Live(spinner, console=console, refresh_per_second=config.CLI_REFRESH_TIME) as live:
            try:
                async for chunk in self.handler.stream_response(
                    payload={"model": self.cfg.model, "messages": self.messages},
                ):
                    if panel is None:
                        panel = Panel(
                            renderable=Markdown(chunk),
                            title="Generating :hourglass_flowing_sand:",
                            subtitle=self.cfg.model,
                            title_align="right",
                            padding=(0, 1),
                            border_style="yellow",
                            expand=False,
                        )
                    else:
                        panel.renderable = Markdown(chunk)
                    live.update(panel)
                if panel is not None:
                    panel.title = f"{self.cfg.role} :heavy_check_mark:"
                    live.update(panel)
                    renderable = panel.renderable
                    if isinstance(renderable, Markdown):
                        return renderable.markup
                    return str(renderable)
            except httpx.ConnectError as error:
                console.log(pformat(error))
            except OllamaError as error:
                console.log(pformat(error))
        return None

    def chat(self, query: str) -> None:
        """Send a message and get a response."""
        self.messages.append({"role": "user", "content": query})
        response = asyncio.run(self._process_response())
        if response:
            self.messages.append({"role": "assistant", "content": response})

    def run(self) -> None:
        """Run the main chat loop."""
        main_panel = Panel(
            renderable=Markdown(assets.WELCOME_MESSAGE + assets.HELP_MESSAGE),
            padding=(0, 1),
            border_style="blue",
            expand=False,
        )
        console.print(main_panel)
        self._preload_current_model()

        while True:
            query = input("> ")
            if query == "/setup":
                main_panel.renderable = Markdown(
                    "\n".join(
                        (
                            "### Current Settings: ",
                            f"- Ollama URL: `{self.cfg.base_url}`",
                            f"- LLM Model Name: **{self.cfg.model}**",
                            f"- Active Role: **{self.cfg.role}**",
                        )
                    )
                )
                console.print(main_panel)
                self.setup()
            elif query == "/help":
                main_panel.renderable = Markdown(assets.HELP_MESSAGE)
                console.print(main_panel)
            elif query == "/model":
                self.select_model()
            elif query == "/roles":
                self.select_role()
            elif query == "/role add":
                self.add_role()
            elif query == "/role delete":
                self.delete_role()
            elif query == "/quit":
                console.print("Goodbye! :wave:")
                break
            elif not query:
                pass
            else:
                self.chat(query)


def main() -> None:
    """Main entry point."""
    session = ChatSession()
    session.run()


if __name__ == "__main__":
    main()
