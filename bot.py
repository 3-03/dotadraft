"""Telegram-бот: подбор контр-пиков в Dota 2 против вражеского драфта.

Запуск:
    1. Получи токен у @BotFather в Telegram.
    2. Скопируй .env.example в .env и вставь токен.
    3. python bot.py
"""

import asyncio
import logging
import os

import httpx
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Update,
    WebAppInfo,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from engine import build_index, format_result, parse_enemies, suggest
from opendota import get_heroes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# HTTPS-ссылка на размещённый Mini App (webapp/index.html). Если не задана —
# бот работает только в текстовом режиме, кнопка приложения не показывается.
WEBAPP_URL = os.getenv("WEBAPP_URL")

HELP_TEXT = (
    "🤖 *Dota Draft Helper*\n\n"
    "Пришли мне героев противника — я подскажу, кем их закрыть.\n\n"
    "Просто перечисли вражеские пики *через запятую*:\n"
    "`Anti-Mage, Invoker, Sniper`\n\n"
    "Можно по-русски и сокращениями: `ам, инвокер, снайпер, па`\n\n"
    "🎮 Или открой приложение с иконками героев: /app\n\n"
    "Данные о матчапах берутся из OpenDota (реальная статистика игр).\n"
    "Команды: /start, /help, /app"
)


async def post_init(app: Application) -> None:
    """Создаёт HTTP-клиент и загружает список героев один раз при старте."""
    client = httpx.AsyncClient(timeout=20.0, headers={"User-Agent": "dota-draft-bot"})
    app.bot_data["client"] = client
    try:
        heroes = await get_heroes(client)
        id_to_name, name_to_id = build_index(heroes)
        app.bot_data["id_to_name"] = id_to_name
        app.bot_data["name_to_id"] = name_to_id
        logger.info("Загружено героев: %d", len(heroes))
    except Exception:  # noqa: BLE001
        logger.exception("Не удалось загрузить список героев при старте")
        app.bot_data["id_to_name"] = {}
        app.bot_data["name_to_id"] = {}

    # Кнопка меню слева от поля ввода открывает Mini App
    if WEBAPP_URL:
        try:
            await app.bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Драфт", web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
            logger.info("Кнопка меню Mini App установлена: %s", WEBAPP_URL)
        except Exception:  # noqa: BLE001
            logger.exception("Не удалось установить кнопку меню Mini App")
    else:
        logger.info("WEBAPP_URL не задан — Mini App отключён, только текстовый режим.")


async def post_shutdown(app: Application) -> None:
    client = app.bot_data.get("client")
    if client is not None:
        await client.aclose()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(HELP_TEXT)


async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет кнопку, открывающую Mini App с иконками героев."""
    if not WEBAPP_URL:
        await update.message.reply_text(
            "Приложение пока не подключено (не задан WEBAPP_URL).\n"
            "Пока просто пришли вражеских героев через запятую, например:\n"
            "Anti-Mage, Invoker, Sniper"
        )
        return
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎮 Открыть драфт-помощник", web_app=WebAppInfo(url=WEBAPP_URL))]]
    )
    await update.message.reply_text(
        "Выбери вражеских героев тапами по иконкам:", reply_markup=keyboard
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    name_to_id = context.bot_data.get("name_to_id") or {}
    id_to_name = context.bot_data.get("id_to_name") or {}
    client = context.bot_data.get("client")

    if not name_to_id or client is None:
        await update.message.reply_text(
            "Список героев ещё не загружен — попробуй через пару секунд ещё раз."
        )
        return

    found, unknown = parse_enemies(text, name_to_id)
    if not found:
        await update.message.reply_text(
            "Не распознал ни одного героя.\n"
            "Перечисли вражеских героев через запятую, например:\n"
            "Anti-Mage, Invoker, Sniper"
        )
        return

    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    try:
        ranked = await suggest(client, found, id_to_name)
    except httpx.HTTPError:
        logger.exception("Ошибка запроса к OpenDota")
        await update.message.reply_text(
            "OpenDota сейчас недоступна или лимит запросов исчерпан. Попробуй позже."
        )
        return

    await update.message.reply_text(format_result(found, unknown, ranked, id_to_name))


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "Не задан BOT_TOKEN. Скопируй .env.example в .env и вставь токен от @BotFather."
        )

    # Python 3.14 больше не создаёт event loop автоматически, а run_polling()
    # в PTB ожидает его наличие в главном потоке — создаём явно.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("app", app_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
