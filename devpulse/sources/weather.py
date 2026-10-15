"""Previsão do tempo via Open-Meteo (API REST gratuita, sem chave)."""
from ..models import Item, Section

URL = "https://api.open-meteo.com/v1/forecast"

# Tradução dos códigos WMO retornados pela API
WMO = {
    0: "céu limpo", 1: "predomínio de sol", 2: "parcialmente nublado", 3: "nublado",
    45: "neblina", 48: "neblina com geada", 51: "garoa fraca", 53: "garoa", 55: "garoa forte",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte", 80: "pancadas fracas",
    81: "pancadas de chuva", 82: "pancadas fortes", 95: "trovoadas", 96: "trovoadas com granizo",
    99: "trovoadas com granizo forte",
}


def fetch(session, config) -> Section:
    from ..http_client import get_json

    data = get_json(session, URL, params={
        "latitude": config.latitude,
        "longitude": config.longitude,
        "current": "temperature_2m,apparent_temperature,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 1,
    })
    now, day = data["current"], data["daily"]
    rain = day["precipitation_probability_max"][0]
    desc = WMO.get(now["weather_code"], "condição desconhecida")

    items = [
        Item(f"{config.city}: {now['temperature_2m']:.0f}°C agora, {desc}",
             detail=f"sensação {now['apparent_temperature']:.0f}°C"),
        Item(f"Mín {day['temperature_2m_min'][0]:.0f}°C / Máx {day['temperature_2m_max'][0]:.0f}°C"),
        Item(f"Chance de chuva: {rain}%" + ("  → leve o guarda-chuva!" if rain >= 50 else "")),
    ]
    return Section("Tempo", "🌤️", items)
