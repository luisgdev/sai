"""Config module."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import tomli_w
import tomllib
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:1b"
DEFAULT_ROLE = "Virtual Assistant"

HTTP_TIMEOUT: int = 60
CLI_REFRESH_TIME: int = 10

CONFIG_DIR = Path(Path.home() / ".sai")
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class OllamaConfig:
    """Ollama configuration settings."""

    base_url: str
    model: str
    role: str = field(default=DEFAULT_ROLE)

    @classmethod
    def _ensure_config_dir(cls) -> None:
        """Create config directory if it doesn't exist."""
        CONFIG_DIR.mkdir(exist_ok=True, parents=True)

    @classmethod
    def _load_toml(cls) -> dict[str, str]:
        """Load TOML config file if it exists."""
        if not CONFIG_FILE.exists():
            return {}
        with open(CONFIG_FILE, "rb") as file_:
            data: dict[str, dict[str, str]] = tomllib.load(file_)
            return data.get("ollama", {})

    @classmethod
    def load(cls) -> Self:
        """Load config with priority: TOML > env vars > defaults."""
        toml_data = cls._load_toml()
        return cls(
            base_url=toml_data.get("base_url") or os.environ.get("OLLAMA_URL", DEFAULT_BASE_URL),
            model=toml_data.get("model") or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL),
            role=toml_data.get("role") or DEFAULT_ROLE,
        )

    def save(self) -> None:
        """Persist configuration to TOML file."""
        self._ensure_config_dir()
        data = {
            "ollama": {
                "base_url": self.base_url,
                "model": self.model,
                "role": self.role,
            }
        }
        with open(CONFIG_FILE, "wb") as file_:
            tomli_w.dump(data, file_)
