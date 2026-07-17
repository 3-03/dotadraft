"""Логика подбора контр-пиков на основе матчапов OpenDota."""

import re

from aliases import CUSTOM_ALIASES
from opendota import get_matchups

# Кандидат учитывается, только если сыграно достаточно игр против врага —
# иначе винрейт статистически недостоверен. Публичная выборка матчапов
# OpenDota небольшая (медиана ~70 игр на пару), поэтому порог невысокий.
MIN_GAMES = 30
# Сколько героев показывать в ответе.
TOP_N = 8


def norm(s: str) -> str:
    """Нормализует имя героя для сопоставления: нижний регистр, только буквы/цифры."""
    return re.sub(r"[^a-zа-я0-9]", "", s.lower())


def build_index(heroes):
    """Строит id->имя и алиас->id из списка героев OpenDota + пользовательских алиасов."""
    id_to_name = {h["id"]: h["localized_name"] for h in heroes}
    name_to_id = {}
    for h in heroes:
        name_to_id[norm(h["localized_name"])] = h["id"]
    # пользовательские алиасы указывают на английское каноническое имя
    for alias, canonical in CUSTOM_ALIASES.items():
        hero_id = name_to_id.get(norm(canonical))
        if hero_id is not None:
            name_to_id[norm(alias)] = hero_id
    return id_to_name, name_to_id


def parse_enemies(text: str, name_to_id):
    """Разбирает сообщение в список id вражеских героев. Возвращает (found_ids, unknown_strings)."""
    parts = re.split(r"[,\n;/|]+", text)
    found = []
    unknown = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        hero_id = name_to_id.get(norm(part))
        if hero_id is not None:
            if hero_id not in found:
                found.append(hero_id)
        else:
            unknown.append(part)
    return found, unknown


async def suggest(client, enemy_ids, id_to_name):
    """Считает преимущество каждого кандидата против вражеского драфта.

    advantage(кандидат, враг) = средний_винрейт_врага - винрейт_врага_против_кандидата.
    То есть насколько хуже среднего этот враг играет против кандидата (>0 => кандидат
    его контрит). База — реальный средний винрейт врага, а не жёсткие 50%, поэтому
    сильные/слабые в целом герои не искажают оценку.

    Ранжирование — по СРЕДНЕМУ преимуществу по всему драфту (отсутствие данных по паре
    считается нейтральным нулём), чтобы вознаграждать героев, закрывающих больше врагов.

    Возвращает список кортежей (candidate_id, avg_advantage, {enemy_id: advantage}).
    """
    # candidate_id -> {enemy_id: advantage}
    per_candidate = {}

    for enemy_id in enemy_ids:
        matchups = await get_matchups(client, enemy_id)
        valid = [m for m in matchups if m["games_played"] >= MIN_GAMES]
        if not valid:
            continue
        total_wins = sum(m["wins"] for m in valid)
        total_games = sum(m["games_played"] for m in valid)
        baseline = total_wins / total_games  # средний винрейт врага

        for m in valid:
            cand_id = m["hero_id"]
            enemy_winrate = m["wins"] / m["games_played"]
            advantage = baseline - enemy_winrate  # >0 => кандидат сильнее врага
            per_candidate.setdefault(cand_id, {})[enemy_id] = advantage

    # своих же врагов из кандидатов убираем
    for enemy_id in enemy_ids:
        per_candidate.pop(enemy_id, None)

    n = len(enemy_ids)
    scored = [
        (cid, sum(per_enemy.values()) / n, per_enemy)
        for cid, per_enemy in per_candidate.items()
    ]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:TOP_N]


def _pct(x: float) -> str:
    """0.061 -> '+6.1%'."""
    return f"{x * 100:+.1f}%"


def format_result(enemy_ids, unknown, ranked, id_to_name) -> str:
    enemy_names = ", ".join(id_to_name.get(e, str(e)) for e in enemy_ids)
    lines = [f"🎯 Контр-пики против: {enemy_names}"]

    if unknown:
        lines.append("⚠️ Не распознал: " + ", ".join(unknown))

    lines.append("")

    if not ranked:
        lines.append("Недостаточно данных, чтобы что-то посоветовать.")
        return "\n".join(lines)

    for i, (cid, avg, per_enemy) in enumerate(ranked, 1):
        name = id_to_name.get(cid, str(cid))
        lines.append(f"{i}. 🛡 {name} — средн. преимущество {_pct(avg)}")
        # разбивка по каждому врагу драфта (от сильного контра к слабому)
        for enemy_id in sorted(enemy_ids, key=lambda e: per_enemy.get(e, -1), reverse=True):
            adv = per_enemy.get(enemy_id)
            ename = id_to_name.get(enemy_id, str(enemy_id))
            if adv is None:
                lines.append(f"   • vs {ename}: нет данных")
            else:
                mark = "✅" if adv > 0 else "▪️"
                lines.append(f"   • vs {ename}: {mark} {_pct(adv)}")
        lines.append("")

    lines.append("Преимущество = насколько ниже своего среднего винрейт врага против этого героя (данные OpenDota).")
    return "\n".join(lines).rstrip()
