# ☕ DevPulse: briefing diário automatizado para devs

Todo dev começa o dia abrindo 5 abas: previsão do tempo, dólar, Hacker News, GitHub Trending...
O **DevPulse** faz isso sozinho: coleta tudo em paralelo e entrega um resumo no terminal,
em uma página HTML e no Telegram, todo dia no horário que você escolher.

## Tecnologias
| Fonte | Técnica | Biblioteca |
|---|---|---|
| Tempo (Open-Meteo) | consumo de API REST | `requests` |
| Cotações (AwesomeAPI) | consumo de API REST | `requests` |
| Hacker News (Firebase API) | API REST + requisições paralelas | `requests`, `ThreadPoolExecutor` |
| GitHub Trending | **web scraping** | `requests` + `beautifulsoup4` |
| Entrega no Telegram | envio via API REST (Bot API) | `requests` |
| Agendamento diário | agendador | `schedule` |

## Destaques técnicos
- Fontes executadas **em paralelo** (`ThreadPoolExecutor`): o briefing sai em ~1 s.
- **Isolamento de falhas**: se uma fonte cair, aparece "indisponível" só naquela seção.
- Sessão HTTP com **retry + backoff exponencial** e timeout.
- Escape de HTML (`html.escape`) para evitar injeção de conteúdo no relatório.
- Parsing separado da coleta, o que permite **testes offline** (`tests/`).

## Como rodar
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # (opcional) configure o Telegram

python main.py                    # terminal + output/briefing.html
python main.py --telegram         # também envia ao Telegram
python main.py --schedule 08:00   # roda todo dia às 08:00
python -m unittest discover -s tests
```

### Criando o bot do Telegram (opcional)
1. No Telegram, fale com **@BotFather** → `/newbot` → copie o token.
2. Envie qualquer mensagem ao seu bot e abra `https://api.telegram.org/bot<TOKEN>/getUpdates`
   para descobrir seu `chat_id`.
3. Preencha `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no `.env`.

## Estrutura
```
main.py              # CLI, orquestração e agendamento
devpulse/
  config.py          # variáveis de ambiente
  http_client.py     # sessão HTTP resiliente
  models.py          # Item e Section
  report.py          # renderização (Telegram/HTML)
  notifiers.py       # Telegram e arquivo HTML
  sources/           # weather, markets, hackernews, trending
tests/               # testes offline
```
