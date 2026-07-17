"""Telegram-бот — лаунчер Mini App «Dota Draft Helper».

Весь подбор контр-пиков происходит внутри Mini App (webapp/index.html).
Бот сам ничего в чате не считает — он показывает снизу постоянные кнопки:
открыть приложение, как пользоваться, автор.

Запуск:
    1. Получи токен у @BotFather в Telegram.
    2. Скопируй .env.example в .env, вставь токен и WEBAPP_URL.
    3. python bot.py
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    MenuButtonWebApp,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# HTTPS-ссылка на размещённый Mini App (webapp/index.html).
WEBAPP_URL = os.getenv("WEBAPP_URL")
GITHUB_URL = "https://github.com/3-03"

# Тексты кнопок нижней клавиатуры
BTN_APP = "🎮 Открыть драфт-помощник"
BTN_HELP = "ℹ️ Как пользоваться"
BTN_AUTHOR = "👤 Автор"

WELCOME = (
    "🛡 *Dota Draft Helper*\n\n"
    "Нажми «🎮 Открыть драфт-помощник» внизу — выбери вражеских героев тапами "
    "по иконкам, и приложение покажет, кем их закрыть.\n\n"
    "Весь подбор — прямо внутри приложения."
)
WELCOME_NO_APP = (
    "🛡 *Dota Draft Helper*\n\n"
    "Приложение пока не подключено (не задан WEBAPP_URL в .env).\n"
    "Разместите папку webapp/ по HTTPS и укажите ссылку — см. README."
)
HELP = (
    "Как пользоваться:\n\n"
    "1. Нажми кнопку «🎮 Открыть драфт-помощник» внизу.\n"
    "2. Тапни по героям, которых пикает противник.\n"
    "3. Нажми «Показать контр-пики».\n\n"
    "Приложение покажет героев, которые их контрят, с преимуществом "
    "по реальной статистике матчапов OpenDota."
)

# Показывается по центру пустого чата ДО нажатия «Запустить» (setMyDescription).
BOT_DESCRIPTION = (
    "🛡 Подскажу, кем закрыть вражеский драфт в Dota 2.\n\n"
    "Открой приложение, отметь героев противника тапами по иконкам — и получи "
    "контр-пиков на основе реальной статистики матчапов OpenDota.\n\n"
    "Нажми «Запустить» и жми кнопку 🎮 снизу."
)
# Короткое описание в профиле бота (setMyShortDescription).
BOT_SHORT_DESCRIPTION = "Контр-пики в Dota 2 по вражескому драфту. Данные OpenDota."


def main_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная клавиатура снизу с заготовленными кнопками."""
    rows = []
    if WEBAPP_URL:
        rows.append([KeyboardButton(BTN_APP, web_app=WebAppInfo(url=WEBAPP_URL))])
    rows.append([KeyboardButton(BTN_HELP), KeyboardButton(BTN_AUTHOR)])
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Открой приложение кнопкой ниже 👇",
    )


async def post_init(app: Application) -> None:
    """Ставит описание бота (по центру пустого чата) и кнопку меню Mini App."""
    try:
        await app.bot.set_my_description(BOT_DESCRIPTION)
        await app.bot.set_my_short_description(BOT_SHORT_DESCRIPTION)
        logger.info("Описание бота установлено.")
    except Exception:  # noqa: BLE001
        logger.exception("Не удалось установить описание бота")

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
        logger.warning("WEBAPP_URL не задан — приложение недоступно, задайте его в .env.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = WELCOME if WEBAPP_URL else WELCOME_NO_APP
    await update.message.reply_markdown(text, reply_markup=main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP, reply_markup=main_keyboard())


async def author_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(
        f"Сделано при поддержке • [3-03]({GITHUB_URL})",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Открыть GitHub", url=GITHUB_URL)]]
        ),
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Реагирует только на заготовленные кнопки; свободный ввод — мягкая подсказка."""
    text = (update.message.text or "").strip()
    if text == BTN_HELP:
        await help_command(update, context)
    elif text == BTN_AUTHOR:
        await author_message(update, context)
    else:
        await update.message.reply_text(
            "Пользуйся кнопками снизу 👇", reply_markup=main_keyboard()
        )


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

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("app", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    logger.info("Бот запущен. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
