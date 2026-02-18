# sai
Simple AI interface to chat with your Ollama models from the terminal

# Features

- [x] Pretty print real time responses in Markdown, using `rich` library.
- [x] Keep conversation context.
- [x] Autodetect and option to select models.
- [ ] Add support for custom prompts.
- [ ] Add conversation persistency (sessions).

# Requirements
An Ollama instance is required to get access to local models. 
By default, the URL is set to `http://localhost:11434`.

# Install
The project is registered in PyPi: https://pypi.org/project/sai-chat/

So you can install it using any package manager of your preference like `pip`, 
but the recommended way is `uv tool`.

## Recommended
Using `uv tool`:

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
│  • /help : Show this help message                     │
│  • /quit : Exit the application                       │
│  • /model : Select a model                            │
╰───────────────────────────────────────────────────────╯
> Hey                               
╭────────────────────────────────────── LLM Response ✔ ─╮
│ What's up? How can I help you today?                  │
╰───────────────────── llama3.2:1b ─────────────────────╯
> 

```

# Status

This project is under development. Feel free to contribute or provide feedback!