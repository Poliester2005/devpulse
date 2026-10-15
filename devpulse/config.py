"""Configuração via variáveis de ambiente / arquivo .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    city: str
    latitude: float
    longitude: float
    hn_limit: int
    trending_limit: int
    trending_language: str
    telegram_token: str | None
    telegram_chat_id: str | None

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_token and self.telegram_chat_id)


def load_config() -> Config:
    load_dotenv()
    return Config(
        city=os.getenv("CITY", "São Paulo"),
        latitude=float(os.getenv("LATITUDE", "-23.5505")),
        longitude=float(os.getenv("LONGITUDE", "-46.6333")),
        hn_limit=int(os.getenv("HN_LIMIT", "5")),
        trending_limit=int(os.getenv("TRENDING_LIMIT", "5")),
        trending_language=os.getenv("TRENDING_LANGUAGE", "python"),
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
    )
