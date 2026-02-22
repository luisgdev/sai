"""Roles module for managing AI personas."""

import tomllib
from dataclasses import dataclass

import tomli_w

from app.config import CONFIG_DIR

ROLES_FILE = CONFIG_DIR / "roles.toml"

DEFAULT_ROLE_NAME = "Virtual Assistant"

PREDEFINED_ROLES: list[dict[str, str]] = [
    {
        "name": "Virtual Assistant",
        "prompt": (
            "You are a friendly virtual assistant. "
            "You are helpful, concise, and provide clear answers."
        ),
    },
    {
        "name": "Marketing Expert",
        "prompt": (
            "You are a marketing expert with deep knowledge of digital marketing, "
            "branding, consumer psychology, and growth strategies. "
            "Provide actionable insights and data-driven recommendations."
        ),
    },
    {
        "name": "Code Reviewer",
        "prompt": (
            "You are a senior code reviewer with expertise in software best practices, "
            "design patterns, and clean code principles. "
            "Focus on code quality, maintainability, security, and performance improvements."
        ),
    },
    {
        "name": "Technical Writer",
        "prompt": (
            "You are a technical writer skilled at explaining complex concepts in simple terms. "
            "You create clear documentation, tutorials, and guides "
            "that are easy to understand for various audiences."
        ),
    },
]


@dataclass
class Role:
    """Represents an AI role/persona."""

    name: str
    prompt: str
    is_predefined: bool = False

    def to_dict(self) -> dict[str, str]:
        """Convert role to dictionary for TOML serialization."""
        return {"name": self.name, "prompt": self.prompt}


class RolesManager:
    """Manages role storage and retrieval."""

    def __init__(self) -> None:
        self._roles: list[Role] | None = None

    @property
    def roles(self) -> list[Role]:
        """Get all roles (predefined + custom)."""
        if self._roles is None:
            self._roles = self._load_roles()
        return self._roles

    def _load_roles(self) -> list[Role]:
        """Load roles from TOML file and merge with predefined."""
        roles: list[Role] = [
            Role(name=r["name"], prompt=r["prompt"], is_predefined=True) for r in PREDEFINED_ROLES
        ]

        custom_roles = self._load_custom_roles()
        roles.extend(custom_roles)

        return roles

    @staticmethod
    def _load_custom_roles() -> list[Role]:
        """Load custom roles from TOML file."""
        if not ROLES_FILE.exists():
            return []

        with open(ROLES_FILE, "rb") as file_:
            data: dict[str, list[dict[str, str]]] = tomllib.load(file_)
            custom = data.get("roles", [])
            return [Role(name=r["name"], prompt=r["prompt"], is_predefined=False) for r in custom]

    def get_by_name(self, name: str) -> Role | None:
        """Get a role by its name."""
        for role in self.roles:
            if role.name == name:
                return role
        return None

    def get_default(self) -> Role:
        """Get the default role."""
        role = self.get_by_name(DEFAULT_ROLE_NAME)
        if role:
            return role
        return self.roles[0]

    def add(self, name: str, prompt: str) -> Role:
        """Add a new custom role."""
        if self.get_by_name(name):
            raise ValueError(f"Role '{name}' already exists")

        role = Role(name=name, prompt=prompt, is_predefined=False)
        self._save_custom_roles([r for r in self.roles if not r.is_predefined] + [role])
        self._roles = None
        return role

    def delete(self, name: str) -> None:
        """Delete a custom role by name."""
        role = self.get_by_name(name)
        if not role:
            raise ValueError(f"Role '{name}' not found")
        if role.is_predefined:
            raise ValueError(f"Cannot delete predefined role '{name}'")

        remaining = [r for r in self.roles if r.name != name and not r.is_predefined]
        self._save_custom_roles(remaining)
        self._roles = None

    @staticmethod
    def _save_custom_roles(roles: list[Role]) -> None:
        """Save custom roles to TOML file."""
        CONFIG_DIR.mkdir(exist_ok=True, parents=True)

        if not roles:
            if ROLES_FILE.exists():
                ROLES_FILE.unlink()
            return

        data = {"roles": [r.to_dict() for r in roles]}
        with open(ROLES_FILE, "wb") as f:
            tomli_w.dump(data, f)

    def list_names(self) -> list[str]:
        """Get list of all role names."""
        return [r.name for r in self.roles]
