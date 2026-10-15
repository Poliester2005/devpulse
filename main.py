"""DevPulse: briefing diário automatizado.

Reúne tempo, cotações, notícias de tecnologia e repositórios em alta e entrega
no terminal, em um arquivo HTML e (opcionalmente) no Telegram.

Uso:
    python main.py                    # imprime no terminal e salva output/briefing.html
    python main.py --telegram         # também envia ao Telegram
    python main.py --schedule 08:00   # fica rodando e envia todo dia às 08:00
"""
# Usa o repositório de certificados do sistema (Windows/macOS) em vez do certifi.
# Resolve redes com proxy/inspeção SSL e servidores com cadeia incompleta.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:  # opcional: sem a lib, usa o comportamento padrão
    pass

import argparse
import html
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor

import schedule

from devpulse import notifiers, report
from devpulse.config import Config, load_config
from devpulse.http_client import build_session
from devpulse.models import Section
from devpulse.sources import hackernews, markets, trending, weather

log = logging.getLogger("devpulse")

# (título, ícone, função de coleta) - o título/ícone são usados se a fonte falhar
SOURCES = [
    ("Tempo", "🌤️", weather.fetch),
    ("Mercado", "💱", markets.fetch),
    ("Hacker News", "📰", hackernews.fetch),
    ("GitHub Trending", "🔥", trending.fetch),
]


def collect(session, config: Config) -> list[Section]:
    """Executa todas as fontes em paralelo. Uma falha não derruba as demais."""

    def safe(source):
        title, icon, fn = source
        try:
            return fn(session, config)
        except Exception as exc:  # noqa: BLE001 - isolamos qualquer erro de fonte
            log.warning("Fonte '%s' falhou: %s", title, exc)
            return Section(title, icon, error=str(exc)[:120])

    with ThreadPoolExecutor(max_workers=len(SOURCES)) as pool:
        return list(pool.map(safe, SOURCES))  # map preserva a ordem


def run(config: Config, use_telegram: bool) -> None:
    session = build_session()
    sections = collect(session, config)

    # 1) Terminal (remove as tags HTML só para leitura)
    print(html.unescape(re.sub(r"<[^>]+>", "", report.render_telegram(sections))))

    # 2) Página HTML
    path = notifiers.save_html(report.render_html_page(sections))
    log.info("Página salva em %s", path.resolve())

    # 3) Telegram (opcional)
    if use_telegram:
        if not config.telegram_enabled:
            log.error("Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env")
            return
        notifiers.send_telegram(session, config.telegram_token, config.telegram_chat_id,
                                report.render_telegram(sections))
        log.info("Briefing enviado ao Telegram")


def main() -> None:
    parser = argparse.ArgumentParser(description="DevPulse - briefing diário para devs")
    parser.add_argument("--telegram", action="store_true", help="envia o briefing ao Telegram")
    parser.add_argument("--schedule", metavar="HH:MM", help="executa todo dia no horário indicado")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("urllib3").setLevel(logging.ERROR)  # silencia logs de retry
    config = load_config()

    if args.schedule:
        schedule.every().day.at(args.schedule).do(run, config, args.telegram)
        log.info("Agendado para todo dia às %s. Ctrl+C para sair.", args.schedule)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run(config, args.telegram)


if __name__ == "__main__":
    main()
