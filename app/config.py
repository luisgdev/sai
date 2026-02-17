"""Config module"""

import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL")

HTTP_TIMEOUT: int = 60
CLI_REFRESH_TIME: int = 10
