from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN, ROOT, TELEGRAM_PROXY
from formatter import format_search_result
from health_server import start_health_server
from proxy_detect import persist_proxy_to_env, resolve_telegram_proxy
from sheets import SheetStore

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

store = SheetStore()
ACTIVE_PROXY: str | None = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Пришли название ТТ (например, Ополченская) — "
        "верну оборудование из таблицы «Список для Эдтех».\n\n"
        "Команды:\n"
        "/start — справка\n"
        "/reload — перезагрузить таблицу"
    )


async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        msg = store.reload()
        await update.message.reply_text(msg)
    except Exception as exc:
        await update.message.reply_text(f"Не удалось загрузить данные: {exc}")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = (update.message.text or "").strip()
    if not query:
        return
    if not store.rows:
        try:
            store.reload()
        except Exception as exc:
            await update.message.reply_text(f"Нет данных: {exc}")
            return

    rows = store.find_by_name(query)
    if not rows:
        await update.message.reply_text(
            f"По запросу «{query}» в столбце name ничего не найдено."
        )
        return

    for part in format_search_result(rows):
        await update.message.reply_text(part)


def main() -> None:
    global ACTIVE_PROXY

    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан в .env / Environment")

    # Render / PaaS: bind health endpoint so the free web service stays reachable
    port_raw = (os.getenv("PORT") or "").strip()
    if port_raw.isdigit():
        start_health_server(int(port_raw))

    try:
        ACTIVE_PROXY, username = resolve_telegram_proxy(BOT_TOKEN, TELEGRAM_PROXY)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    on_render = bool(os.getenv("RENDER"))
    if (
        not on_render
        and ACTIVE_PROXY
        and ACTIVE_PROXY != TELEGRAM_PROXY
    ):
        persist_proxy_to_env(ROOT / ".env", ACTIVE_PROXY)
        logger.info("Saved working proxy to .env: %s", ACTIVE_PROXY)

    logger.info("Telegram OK: @%s (proxy=%s)", username, ACTIVE_PROXY or "direct")

    try:
        status = store.reload()
        logger.info(status)
    except Exception as exc:
        logger.error("Initial data load failed: %s", exc)

    builder = Application.builder().token(BOT_TOKEN)
    if ACTIVE_PROXY:
        builder = builder.proxy(ACTIVE_PROXY).get_updates_proxy(ACTIVE_PROXY)

    app = builder.build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reload", reload_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
