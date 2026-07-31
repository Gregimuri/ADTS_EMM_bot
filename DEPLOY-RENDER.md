# Деплой на Render (бесплатный Web Service)

Polling-бот на **Free Web Service**. Background Worker на free-тарифе нет.

На free инстанс **засыпает через ~15 минут без HTTP-запросов**.  
Поэтому нужен keep-alive: пинг URL бота раз в 10 минут (ниже).

Лимит: **750 free hours / месяц** — при круглосуточном keep-alive почти весь месяц, дальше сервис встанет до следующего месяца (или апгрейд).

## 1. GitHub

1. Создайте репозиторий на GitHub (Private нормально).
2. Залейте **только код бота** (не `.env`, не `.venv`):

Файлы: `bot.py`, `config.py`, `sheets.py`, `formatter.py`, `proxy_detect.py`, `health_server.py`, `requirements.txt`, `runtime.txt`, `render.yaml`, …

В PowerShell из папки проекта (если git ещё не инициализирован здесь):

```powershell
cd "C:\Users\Григорий\Desktop\Бот по ЕММ"
git init
git add bot.py config.py sheets.py formatter.py proxy_detect.py health_server.py requirements.txt runtime.txt render.yaml .env.example .gitignore README.md DEPLOY-RENDER.md deploy
git commit -m "EMM Telegram bot for Render"
# затем создайте repo на GitHub и:
# git remote add origin https://github.com/USER/REPO.git
# git branch -M main
# git push -u origin main
```

`.env` в git не попадает (уже в `.gitignore`).

## 2. Сервис на Render

1. https://dashboard.render.com → **New** → **Blueprint** (если есть `render.yaml`)  
   **или** **New** → **Web Service** → подключите GitHub-репозиторий.
2. Настройки:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Instance type:** Free
3. **Environment** → добавьте:

| Key | Value |
|-----|--------|
| `BOT_TOKEN` | токен от BotFather |
| `TELEGRAM_PROXY` | *(пусто)* |
| `SPREADSHEET_ID` | `12aHPQbN65UBk6vlxiDB_nCg9V_xSbrbms70X3xqABKQ` |
| `SHEET_GID` | `58485295` |

4. **Create Web Service** → дождитесь Deploy live.
5. В логах должны быть: `Health server listening`, `Telegram OK`, `Bot started`.

## 3. Keep-alive (обязательно на Free)

Скопируйте URL сервиса, например `https://emm-bot-xxxx.onrender.com`.

1. Откройте https://cron-job.org (бесплатно) или любой другой cron.
2. Создайте задачу: **каждые 10 минут**, метод GET, URL вашего сервиса.
3. Без этого бот заснёт, и ответы появятся только после «пробуждения» (~1 мин).

## 4. Важно

- **Остановите бота на своём ПК** (`Ctrl+C` / закройте окно) — два экземпляра дадут Conflict.
- На Render прокси не нужен.
- Excel на сервер копировать не нужно — данные с Google Sheets.
- Если нужен бот **без засыпаний и без лимита 750 ч** — Worker Starter (~$7/мес) или Oracle Always Free ([DEPLOY-ORACLE.md](DEPLOY-ORACLE.md)).

## 5. Обновление кода

```powershell
git add -A
git commit -m "update bot"
git push
```

Render подхватит push и задеплоит сам (если Auto-Deploy включён).
