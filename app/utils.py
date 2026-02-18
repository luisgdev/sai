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
    return answers["value"]


def text_input(message: str) -> str:
    """Display a text input interface in the terminal."""
    question = inquirer.Text(
        name="value",
        message=message,
    )
    answers = inquirer.prompt([question])
    return answers["value"]
