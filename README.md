# sai
Simple AI interface to chat with your Ollama models from the terminal

# Features

- [x] Pretty print real time responses in Markdown, using `rich` library.
- [x] Keep conversation context.
- [x] Autodetect and option to select models.
- [x] Add support for custom prompts.
- [x] Add custom roles (reusable prompts).
- [x] Improve performance by preloading models.
- [ ] Add conversation persistency (sessions).

# Requirements
An Ollama instance is required to get access to local models. 
By default, the URL is set to `http://localhost:11434`.

# Install
You can install it using any package manager of your preference like `pip`, 
but the recommended way is `uv tool`.

## Recommended
Using `uv`:

```shell
uv tool install sai-chat
```

# Usage

Start using it in your terminal just by running `sai` command:
```shell
luis@laptop:~ $ sai
╭───────────────────────────────────────────────────────╮
│ Welcome to Sai. Chat with your local LLM models.      │
│                                                       │
│ Available commands:                                   │
│                                                       │
│  • /setup : Setup Ollama URL and preferences          │
│  • /model : Select a model                            │
│  • /roles : List and select a role                    │
│  • /role add : Create a new custom role               │
│  • /role delete : Delete a custom role                │
│  • /help : Show this help message                     │
│  • /quit : Exit the application                       │
╰───────────────────────────────────────────────────────╯
> hi
╭───────────────────────────────── Virtual Assistant ✔ ─╮
│ Hi there! How can I help you today? 😊                │
╰────────────────────── gemma3:1b ──────────────────────╯
> 

```

# Status

This project is under development. Feel free to contribute or provide feedback!