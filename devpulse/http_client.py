"""Sessão HTTP resiliente: timeout, retry com backoff e User-Agent próprio."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT = 10  # segundos


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,                       # 0.5s, 1s, 2s...
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "DevPulse/1.0 (projeto academico)"})
    return session


def get_json(session: requests.Session, url: str, **kwargs):
    """GET que levanta erro em status != 2xx e devolve o JSON."""
    response = session.get(url, timeout=TIMEOUT, **kwargs)
    response.raise_for_status()
    return response.json()
