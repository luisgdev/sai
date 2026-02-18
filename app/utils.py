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
