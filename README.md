# ADTS EMM Bot

Telegram-бот для поиска оборудования торговых точек (ТТ) по данным из Google Таблицы **«База для бота»**.  
Пользователь отправляет название или часть названия ТТ — бот возвращает сгруппированный список плееров: PlayerId, модель, ЕММ, ADB, кубик, MAC и прочие поля.

**Продакшен:** [@ADTS_EMM_bot](https://t.me/ADTS_EMM_bot) (Render).

## Возможности

- Поиск по подстроке в столбце `name` (без учёта регистра)
- Группировка устройств по торговой точке
- Компактный формат ответа (статусы ✅ / ❌, блоки по устройствам)
- Автоматическая пометка **«Ничего не делать»**, если в таблице так указано или одновременно **ЕММ: не ставить** и **Кубик: Обновить удалённо**
- Загрузка данных из Google Sheets (CSV) с запасным вариантом — локальный Excel
- На ПК в РФ: автоподбор SOCKS/HTTP-прокси до Telegram API
- Для хостинга: HTTP `/` (GET/HEAD) для health-check и keep-alive

## Источник данных

| Параметр | Значение |
|----------|----------|
| Таблица | [База для бота](https://docs.google.com/spreadsheets/d/1sRy5VuFGEWsh_RZCGUkWKyKcLP8i6dO-F1smi4ok4Mk/edit?gid=0) |
| Лист | **ЕММ (Список плееров)** (`gid=0`) |

Таблица должна быть доступна **по ссылке** с ролью **Читатель** (экспорт CSV без OAuth).

Ожидаемые столбцы (порядок важен): `objectNumber`, `Адрес`, `playerId`, `name`, `ЕММ`, `Перепрошить`, `Модель`, `подключение по adb`, `Обновить Кубик`, `Ничего не делать`, `Версия старая`, `Эдтех`, `network.macAddress`.

## Стек

- Python 3.10+
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/) 22.x (long polling)
- httpx, openpyxl, python-dotenv

## Структура репозитория

| Файл / каталог | Назначение |
|----------------|------------|
| `bot.py` | Точка входа, хендлеры, polling |
| `config.py` | Переменные окружения и константы столбцов |
| `sheets.py` | Загрузка таблицы и поиск |
| `formatter.py` | Форматирование ответов в Telegram |
| `proxy_detect.py` | Проверка Telegram и автопоиск локального прокси |
| `health_server.py` | HTTP health для Render / UptimeRobot |
| `render.yaml` | Blueprint деплоя на Render |
| `deploy/` | systemd и скрипт установки (Oracle / VPS) |
| `DEPLOY-RENDER.md`, `DEPLOY-ORACLE.md` | Подробные инструкции по хостингу |

## Быстрый старт (локально, Windows)

```powershell
cd "путь\к\проекту"
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# заполните BOT_TOKEN в .env
.\.venv\Scripts\python.exe bot.py
```

Или запуск через `start.bat`.

> Используйте Python из `.venv`. Системный `python` без зависимостей даст ошибку вида `No module named 'httpx'`.

## Переменные окружения

Скопируйте `.env.example` в `.env` или задайте переменные на хостинге:

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `BOT_TOKEN` | да | Токен от [@BotFather](https://t.me/BotFather) |
| `SPREADSHEET_ID` | нет | ID Google Таблицы (есть значение по умолчанию) |
| `SHEET_GID` | нет | ID листа (`0` для «ЕММ (Список плееров)») |
| `TELEGRAM_PROXY` | нет | Прокси к `api.telegram.org` (`socks5://…` или `http://…`). На Render обычно пусто |
| `LOCAL_XLSX` | нет | Имя запасного Excel в каталоге проекта |

Пример `.env` для текущей таблицы:

```env
BOT_TOKEN=ваш_токен
SPREADSHEET_ID=1sRy5VuFGEWsh_RZCGUkWKyKcLP8i6dO-F1smi4ok4Mk
SHEET_GID=0
TELEGRAM_PROXY=
```

## Команды бота

| Команда | Действие |
|---------|----------|
| `/start` | Краткая справка |
| `/reload` | Перечитать данные из Google (при ошибке — из Excel) |
| *текст* | Поиск по столбцу `name` |

## Деплой 24/7

Основной вариант — **Render** (Free Web Service + keep-alive):

- Инструкция: [DEPLOY-RENDER.md](DEPLOY-RENDER.md)
- В Environment на Render: `BOT_TOKEN`, `SPREADSHEET_ID`, `SHEET_GID`, пустой `TELEGRAM_PROXY`
- Обязателен keep-alive (UptimeRobot / GitHub Actions), иначе free-инстанс засыпает

Альтернатива — VPS Oracle Cloud: [DEPLOY-ORACLE.md](DEPLOY-ORACLE.md)

**Важно:** одновременно должен работать только **один** экземпляр бота (иначе `Conflict` в Telegram).

## Если бот не отвечает (РФ, локальный запуск)

Часто блокируется `api.telegram.org`, при этом Google Sheets доступен.

1. Включите VPN или укажите прокси клиента в `TELEGRAM_PROXY` (типичные порты: `10808`, `7890`).
2. При старте бот сам проверяет Telegram; при успехе может сохранить рабочий прокси в `.env`.
3. Не запускайте второй экземпляр параллельно с Render.

## Репозитории

| Remote | URL |
|--------|-----|
| GitHub | https://github.com/Gregimuri/ADTS_EMM_bot |
| GitLab | https://gitlab.remosa.ru/adts-platform/adts_emm_bot |

## Безопасность

Токен бота храните только в `.env` / секретах хостинга, не коммитьте в git.  
При утечке токена — `/revoke` в BotFather и новый токен в настройках.

## Лицензия

Внутренний инструмент ADTS. При публикации уточните лицензию у владельца репозитория.