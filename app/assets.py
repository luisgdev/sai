"""Assets module"""

WELCOME_MESSAGE = """
Welcome to Sai. Chat with your local LLM models.
"""

COMMANDS = {
    "/setup": "Settings and preferences",
    "/model": "List and select a model",
    "/roles": "List and select a role",
    "/role add": "Add a new custom role",
    "/role delete": "Delete a custom role",
    "/help": "Show this help message",
    "/quit": "Exit the application",
}

HELP_MESSAGE = """
### Available commands:\n
"""

for key, val in COMMANDS.items():
    HELP_MESSAGE += f"- `{key}` - {val}\n"

CURRENT_SETTINGS = """
### Current Settings:
- Ollama URL : `{url}`
- Model Name : **{model}**
- Active Role : *{role}*
"""
