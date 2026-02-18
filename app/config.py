"""Config module"""

import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

HTTP_TIMEOUT: int = 60
CLI_REFRESH_TIME: int = 10
