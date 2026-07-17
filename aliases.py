"""Пользовательские алиасы: русские названия и сокращения -> английское имя героя.

Английские имена (localized_name) распознаются автоматически из OpenDota,
здесь только то, что удобно вводить по-русски или сокращённо.
Ключ и значение нормализуются (нижний регистр, без пробелов/дефисов),
поэтому регистр и пробелы тут не важны.
"""

CUSTOM_ALIASES = {
    # Anti-Mage
    "ам": "Anti-Mage", "антимаг": "Anti-Mage", "маг": "Anti-Mage", "am": "Anti-Mage",
    # Phantom Assassin
    "па": "Phantom Assassin", "pa": "Phantom Assassin", "фантомка": "Phantom Assassin",
    # Phantom Lancer
    "пл": "Phantom Lancer", "pl": "Phantom Lancer",
    # Juggernaut
    "джаг": "Juggernaut", "джага": "Juggernaut", "jug": "Juggernaut", "джагернаут": "Juggernaut",
    # Sniper
    "снайпер": "Sniper", "снап": "Sniper",
    # Drow Ranger
    "дров": "Drow Ranger", "дроу": "Drow Ranger", "drow": "Drow Ranger",
    # Faceless Void
    "войд": "Faceless Void", "void": "Faceless Void", "фейслес": "Faceless Void",
    # Invoker
    "инвокер": "Invoker", "инвок": "Invoker", "инвойкер": "Invoker",
    # Pudge
    "пудж": "Pudge", "пудга": "Pudge",
    # Crystal Maiden
    "кристалка": "Crystal Maiden", "цм": "Crystal Maiden", "cm": "Crystal Maiden",
    # Lion / Lina / Lich
    "лион": "Lion", "лина": "Lina", "лич": "Lich",
    # Shadow Fiend
    "сф": "Shadow Fiend", "sf": "Shadow Fiend", "шадоу": "Shadow Fiend",
    # Storm / Ember / Void spirits
    "шторм": "Storm Spirit", "storm": "Storm Spirit",
    "эмбер": "Ember Spirit", "ember": "Ember Spirit",
    "войд спирит": "Void Spirit",
    # Templar Assassin
    "та": "Templar Assassin", "ta": "Templar Assassin", "темпларка": "Templar Assassin",
    # Queen of Pain
    "квопа": "Queen of Pain", "qop": "Queen of Pain",
    # Outworld Destroyer
    "од": "Outworld Destroyer", "od": "Outworld Destroyer", "оутворлд": "Outworld Destroyer",
    # Nature's Prophet
    "нп": "Nature's Prophet", "np": "Nature's Prophet", "фурион": "Nature's Prophet",
    # Windranger
    "вр": "Windranger", "wr": "Windranger", "винда": "Windranger", "ветра": "Windranger",
    # Zeus
    "зевс": "Zeus", "зеус": "Zeus",
    # Wraith King
    "вк": "Wraith King", "wk": "Wraith King", "рейт": "Wraith King", "скелетон": "Wraith King",
    # Spectre / Terrorblade / Medusa
    "спектра": "Spectre", "спектр": "Spectre",
    "тб": "Terrorblade", "tb": "Terrorblade", "терр": "Terrorblade",
    "медуза": "Medusa", "медуза сирена": "Medusa",
    # Lifestealer
    "лайф": "Lifestealer", "нага лайф": "Lifestealer", "лс": "Lifestealer",
    # Sven / Slark / Ursa
    "свен": "Sven", "сларк": "Slark", "урса": "Ursa", "медведь": "Ursa",
    # Bristleback / Timbersaw / Necrophos
    "бристл": "Bristleback", "бб": "Bristleback", "bb": "Bristleback",
    "тимбер": "Timbersaw", "timber": "Timbersaw",
    "некр": "Necrophos", "некрофос": "Necrophos", "necro": "Necrophos",
    # Huskar / Zeus / Tinker / Riki
    "хускар": "Huskar", "тинкер": "Tinker", "рики": "Riki",
    # Bloodseeker / Axe / Legion
    "бс": "Bloodseeker", "кровосос": "Bloodseeker",
    "акс": "Axe", "топор": "Axe",
    "легион": "Legion Commander", "лега": "Legion Commander", "lc": "Legion Commander",
    # Nyx / Bane / Silencer / Doom / Disruptor
    "никс": "Nyx Assassin", "нюкс": "Nyx Assassin",
    "бейн": "Bane", "сайленсер": "Silencer", "сая": "Silencer",
    "дум": "Doom", "дизраптор": "Disruptor",
    # Weaver / Clinkz / Meepo / Brood / Naga
    "вивер": "Weaver", "клинкз": "Clinkz", "мипо": "Meepo",
    "брудка": "Broodmother", "брод": "Broodmother",
    "нага": "Naga Siren",
    # Luna / Gyro / Troll / Monkey / Razor / Morph
    "луна": "Luna", "гиро": "Gyrocopter", "гира": "Gyrocopter",
    "тролль": "Troll Warlord", "тролл": "Troll Warlord",
    "манки": "Monkey King", "мк": "Monkey King", "обезьяна": "Monkey King",
    "рейзор": "Razor",
    "морф": "Morphling", "морфлинг": "Morphling",
    # Death Prophet / Viper / Puck / Ember
    "дп": "Death Prophet", "dp": "Death Prophet",
    "випер": "Viper", "гадюка": "Viper",
    "пак": "Puck", "пака": "Puck",
    # Slardar / Clockwerk / Spirit Breaker / Tusk
    "слардар": "Slardar", "клок": "Clockwerk", "клокверк": "Clockwerk",
    "сб": "Spirit Breaker", "барабака": "Spirit Breaker", "бара": "Spirit Breaker",
    "туск": "Tusk",
    # Kunkka / Centaur / Dragon Knight
    "кунка": "Kunkka", "центавр": "Centaur Warrunner", "кентавр": "Centaur Warrunner",
    "дк": "Dragon Knight", "dk": "Dragon Knight", "дракон": "Dragon Knight",
    # Night Stalker / Ancient Apparition
    "нс": "Night Stalker", "найтсталкер": "Night Stalker",
    "аа": "Ancient Apparition", "aa": "Ancient Apparition", "апарка": "Ancient Apparition",
}
