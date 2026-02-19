"""Utility functions."""
import inquirer


def item_selection_input(message: str, items: list[str]) -> str:
    """Display a selection interface in the terminal."""
    question = inquirer.List(
        name="value",
        message=message,
        choices=items,
    )
    answers = inquirer.prompt([question])
    if not answers:
        raise KeyboardInterrupt("Selection cancelled by user")
    return answers["value"]  # type: ignore[no-any-return]


def text_input(message: str) -> str | None:
    """Display a text input interface in the terminal."""
    question = inquirer.Text(
        name="value",
        message=message,
    )
    answers = inquirer.prompt([question])
    if not answers:
        return None
    return answers["value"]  # type: ignore[no-any-return]
