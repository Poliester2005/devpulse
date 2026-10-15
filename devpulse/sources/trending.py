"""Repositórios em alta no GitHub: web scraping com BeautifulSoup.

O GitHub não tem API oficial para o Trending, então raspamos o HTML da página.
Se o layout mudar, a seção falha de forma isolada e o resto do briefing segue.
"""
from bs4 import BeautifulSoup

from ..http_client import TIMEOUT
from ..models import Item, Section

URL = "https://github.com/trending/{language}?since=daily"


MAX_DESC = 110  # descrições longas atrapalham a leitura


def parse(html: str, limit: int) -> list[Item]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for repo in soup.select("article.Box-row")[:limit]:
        link = repo.select_one("h2 a")
        if not link:
            continue
        name = "".join(link.get_text().split())          # "user / repo" -> "user/repo"
        desc_tag = repo.select_one("p")
        desc = " ".join(desc_tag.get_text().split()) if desc_tag else "Sem descrição"
        if len(desc) > MAX_DESC:
            desc = desc[: MAX_DESC - 1].rstrip() + "…"
        today = repo.select_one("span.d-inline-block.float-sm-right")
        stars = " ".join(today.get_text().split()) if today else ""
        items.append(Item(
            text=f"{name}: {desc}",
            url="https://github.com" + link["href"],
            detail=stars,
        ))
    return items


def fetch(session, config) -> Section:
    response = session.get(URL.format(language=config.trending_language), timeout=TIMEOUT)
    response.raise_for_status()
    title = f"GitHub Trending ({config.trending_language})"
    return Section(title, "🔥", parse(response.text, config.trending_limit))
