"""Destinos do briefing: Telegram (REST) e arquivo HTML local."""
from pathlib import Path

TELEGRAM_LIMIT = 4000  # a API aceita 4096 caracteres por mensagem; deixamos margem


def _chunks(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Quebra o texto em blocos <= limit, sempre em separadores de seção."""
    chunks, current = [], ""
    for block in text.split("\n\n"):
        if current and len(current) + len(block) + 2 > limit:
            chunks.append(current)
            current = block
        else:
            current = f"{current}\n\n{block}" if current else block
    if current:
        chunks.append(current)
    return chunks


def send_telegram(session, token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chunk in _chunks(text):
        response = session.post(url, timeout=10, json={
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
        response.raise_for_status()


def save_html(html: str, path: str = "output/briefing.html") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target
