"""Top histórias do Hacker News (API Firebase oficial).

Para cada ID de história é preciso uma requisição extra, então as buscas
rodam em paralelo com ThreadPoolExecutor.
"""
from concurrent.futures import ThreadPoolExecutor

from ..http_client import get_json
from ..models import Item, Section

BASE = "https://hacker-news.firebaseio.com/v0"
HN_ITEM_PAGE = "https://news.ycombinator.com/item?id={}"


def fetch(session, config) -> Section:
    ids = get_json(session, f"{BASE}/topstories.json")[: config.hn_limit]
    with ThreadPoolExecutor(max_workers=len(ids) or 1) as pool:
        stories = list(pool.map(lambda i: get_json(session, f"{BASE}/item/{i}.json"), ids))

    items = [
        Item(
            text=story["title"],
            # Posts sem link externo (Ask HN etc.) apontam para a discussão
            url=story.get("url") or HN_ITEM_PAGE.format(story["id"]),
            detail=f"{story.get('score', 0)} pts · {story.get('descendants', 0)} comentários",
        )
        for story in stories if story
    ]
    return Section("Hacker News", "📰", items)
