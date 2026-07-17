"""Офлайн-проверка движка без Telegram: подбор против тестового драфта."""

import asyncio

import httpx

from engine import build_index, format_result, parse_enemies, suggest
from opendota import get_heroes


async def main():
    async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": "dota-draft-bot"}) as client:
        heroes = await get_heroes(client)
        id_to_name, name_to_id = build_index(heroes)
        print(f"Героев загружено: {len(heroes)}")

        draft = "Anti-Mage, Invoker, Sniper, ам, несуществующийгерой"
        found, unknown = parse_enemies(draft, name_to_id)
        print("Распознаны id:", found, "->", [id_to_name[i] for i in found])
        print("Не распознаны:", unknown)

        ranked = await suggest(client, found, id_to_name)
        print("\n" + format_result(found, unknown, ranked, id_to_name))


if __name__ == "__main__":
    asyncio.run(main())
