"""Cotações (dólar, euro, bitcoin) via AwesomeAPI (REST gratuita, sem chave)."""
from ..models import Item, Section

URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL"
LABELS = {"USDBRL": "Dólar", "EURBRL": "Euro", "BTCBRL": "Bitcoin"}


def parse(data: dict) -> list[Item]:
    """Converte a resposta da API em itens. Separado do fetch para facilitar testes."""
    items = []
    for key, label in LABELS.items():
        quote = data.get(key)
        if not quote:
            continue
        bid = float(quote["bid"])
        change = float(quote["pctChange"])
        arrow = "▲" if change > 0 else "▼" if change < 0 else "■"
        # Formato brasileiro: 1.234,56
        price = f"{bid:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        items.append(Item(f"{label}: R$ {price}", detail=f"{arrow} {change:+.2f}%"))
    return items


def fetch(session, config) -> Section:
    from ..http_client import get_json

    return Section("Mercado", "💱", parse(get_json(session, URL)))
