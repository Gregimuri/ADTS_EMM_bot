from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
# HTTP/HTTPS/SOCKS5 proxy for Telegram API, e.g. socks5://127.0.0.1:10808
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY", "").strip()
# Google: «База для бота», лист «ЕММ (Список плееров)» (gid=0)
SPREADSHEET_ID = os.getenv(
    "SPREADSHEET_ID",
    "1sRy5VuFGEWsh_RZCGUkWKyKcLP8i6dO-F1smi4ok4Mk",
).strip()
SHEET_GID = os.getenv("SHEET_GID", "0").strip()
LOCAL_XLSX = ROOT / os.getenv("LOCAL_XLSX", "База для бота.xlsx")

COLUMNS = (
    "objectNumber",
    "Адрес",
    "playerId",
    "name",
    "ЕММ",
    "Перепрошить",
    "Модель",
    "подключение по adb",
    "Обновить Кубик",
    "Ничего не делать",
    "Версия старая",
    "Эдтех",
    "network.macAddress",
)
