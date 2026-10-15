"""Modelos de dados compartilhados entre fontes, relatório e notificadores."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    """Uma linha do briefing (ex.: uma notícia, uma cotação)."""
    text: str
    url: str | None = None   # link opcional
    detail: str = ""         # informação secundária (pontos, estrelas, variação...)


@dataclass
class Section:
    """Um bloco do briefing, produzido por uma fonte de dados."""
    title: str
    icon: str
    items: list[Item] = field(default_factory=list)
    error: str | None = None  # preenchido quando a fonte falha (o resto segue funcionando)
