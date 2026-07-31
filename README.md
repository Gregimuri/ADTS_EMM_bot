# Бот ЕММ / Эдтех

Telegram-бот: пишешь название ТТ (например, `Ополченская`), бот ищет совпадения в столбце **name** Google Таблицы и отвечает списком оборудования.

## Быстрый старт

1. Открой доступ к таблице:
   - [Список для Эдтех](https://docs.google.com/spreadsheets/d/12aHPQbN65UBk6vlxiDB_nCg9V_xSbrbms70X3xqABKQ/edit?gid=58485295)
   - «Настройки доступа» → «Все, у кого есть ссылка» → роль **Читатель**
2. В `.env` укажи `BOT_TOKEN` (и при необходимости `TELEGRAM_PROXY`).
3. Запуск:
   - двойной клик по `start.bat`, **или** из папки проекта:

```bat
.venv\Scripts\python.exe bot.py
```

В PowerShell:

```powershell
.\.venv\Scripts\python.exe bot.py
```

Не используй системный `python` без `.venv` — будет ошибка `No module named 'httpx'`.

## Команды

- `/start` — справка
- `/reload` — перечитать таблицу (Google, иначе Excel)

## Настройки

Файл `.env`:

- `BOT_TOKEN` — токен от BotFather
- `TELEGRAM_PROXY` — SOCKS5/HTTP прокси к Telegram (опционально)
- `SPREADSHEET_ID` / `SHEET_GID` — id таблицы и листа
- `LOCAL_XLSX` — запасной Excel

## Если бот не отвечает

Частая причина в РФ: **сеть блокирует `api.telegram.org`** (Google Таблица при этом работает).

1. Включи VPN на ПК **или** укажи прокси клиента VPN в `.env`:

```env
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

или

```env
TELEGRAM_PROXY=http://127.0.0.1:7890
```

Порт смотри в настройках VPN (Clash / Hiddify / Outline / v2rayN и т.п.).

2. Запускай **только один** экземпляр `python bot.py`.

При старте бот сам проверяет доступ к Telegram и пишет ошибку, если связи нет.

## Важно про токен

Если токен светился в переписке или попал в логи — отзови его в [@BotFather](https://t.me/BotFather) (`/revoke`) и пропиши новый в `.env`.

## Постоянная работа 24/7

- **Render (выбранный вариант):** [DEPLOY-RENDER.md](DEPLOY-RENDER.md)
- **Oracle Cloud Always Free:** [DEPLOY-ORACLE.md](DEPLOY-ORACLE.md)
