"""Тонкая обёртка над публичным OpenDota API с файловым кэшем.

Документация: https://docs.opendota.com/
Без ключа доступно ~2000 запросов в день / 60 в минуту — нам с запасом хватает,
т.к. ответы кэшируются на диск.
"""

import json
import os
import time

import httpx

BASE = "https://api.opendota.com/api"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

HERO_TTL = 24 * 3600        # список героев меняется редко
MATCHUP_TTL = 12 * 3600     # статистика матчапов обновляется медленно

os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(name: str) -> str:
    return os.path.join(CACHE_DIR, name)


def _read_cache(name: str, ttl: int):
    path = _cache_path(name)
    if os.path.exists(path) and (time.time() - os.path.getmtime(path) < ttl):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _write_cache(name: str, data) -> None:
    try:
        with open(_cache_path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass


async def get_heroes(client: httpx.AsyncClient):
    """Список всех героев: [{id, localized_name, ...}, ...]."""
    cached = _read_cache("heroes.json", HERO_TTL)
    if cached:
        return cached
    resp = await client.get(f"{BASE}/heroes")
    resp.raise_for_status()
    data = resp.json()
    _write_cache("heroes.json", data)
    return data


async def get_matchups(client: httpx.AsyncClient, hero_id: int):
    """Матчапы героя против всех остальных: [{hero_id, games_played, wins}, ...].

    wins — победы ГЕРОЯ hero_id в играх, где он стоял против hero_id из записи.
    Значит winrate = wins / games_played — это винрейт нашего вражеского героя
    против кандидата. Чем он ниже, тем сильнее кандидат его контрит.
    """
    name = f"matchups_{hero_id}.json"
    cached = _read_cache(name, MATCHUP_TTL)
    if cached:
        return cached
    resp = await client.get(f"{BASE}/heroes/{hero_id}/matchups")
    resp.raise_for_status()
    data = resp.json()
    _write_cache(name, data)
    return data
