"""Repository module"""

from pathlib import Path

from peewee import CharField, Model, SqliteDatabase

from app import config

DATABASE_DIR = Path(Path.home() / ".sai")
DATABASE_DIR.mkdir(exist_ok=True, parents=True)
db = SqliteDatabase(Path(DATABASE_DIR / "sai_chat.db"))


class BaseModel(Model):
    """Base model for all models"""

    class Meta:
        """Meta props"""

        database = db


class OllamaSettings(BaseModel):
    """Ollama settings model"""

    base_url = CharField()
    model_name = CharField()


class Role(BaseModel):
    """Role model to define custom prompts"""

    name = CharField()
    prompt = CharField()
    model_name = CharField()


def _init_db():
    """Initialize database"""
    db.connect()
    db.create_tables([OllamaSettings, Role])


def get_ollama_settings():
    """Get Ollama settings"""
    _init_db()
    try:
        settings = OllamaSettings.get(id=1)
    except OllamaSettings.DoesNotExist:
        settings = OllamaSettings.create(
            base_url=config.OLLAMA_URL, model_name=config.OLLAMA_MODEL
        )
    return settings


if __name__ == "__main__":
    _init_db()
