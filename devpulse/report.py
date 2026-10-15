"""Renderização do briefing em HTML (Telegram) e em página HTML completa."""
from datetime import datetime
from html import escape

from .models import Section

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def _today_label() -> str:
    now = datetime.now()
    return f"{DIAS[now.weekday()]}, {now:%d/%m/%Y}"


def render_telegram(sections: list[Section]) -> str:
    """Texto no subconjunto de HTML aceito pelo Telegram (b, a, i)."""
    blocks = [f"<b>☕ DevPulse · {_today_label()}</b>"]
    for sec in sections:
        lines = [f"<b>{sec.icon} {escape(sec.title)}</b>"]
        if sec.error:
            lines.append(f"<i>⚠️ indisponível: {escape(sec.error)}</i>")
        for item in sec.items:
            text = escape(item.text)
            if item.url:
                text = f'<a href="{escape(item.url, quote=True)}">{text}</a>'
            if item.detail:
                text += f" <i>({escape(item.detail)})</i>"
            lines.append("• " + text)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


CSS = """
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;max-width:760px;margin:2rem auto;padding:0 1rem}
h1{font-size:1.6rem} section{background:#1e293b;border-radius:12px;padding:1rem 1.4rem;margin:1rem 0}
h2{margin:.2rem 0 .6rem;font-size:1.15rem} li{margin:.35rem 0} a{color:#38bdf8;text-decoration:none}
a:hover{text-decoration:underline} small{color:#94a3b8} .err{color:#fca5a5}
"""


def render_html_page(sections: list[Section]) -> str:
    parts = [
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>",
        "<title>DevPulse</title>", f"<style>{CSS}</style></head><body>",
        f"<h1>☕ DevPulse · {_today_label()}</h1>",
    ]
    for sec in sections:
        parts.append(f"<section><h2>{sec.icon} {escape(sec.title)}</h2><ul>")
        if sec.error:
            parts.append(f"<li class='err'>⚠️ indisponível: {escape(sec.error)}</li>")
        for item in sec.items:
            text = escape(item.text)
            if item.url:
                text = f"<a href='{escape(item.url, quote=True)}'>{text}</a>"
            detail = f" <small>({escape(item.detail)})</small>" if item.detail else ""
            parts.append(f"<li>{text}{detail}</li>")
        parts.append("</ul></section>")
    parts.append("</body></html>")
    return "\n".join(parts)
