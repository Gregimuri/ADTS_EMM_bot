#!/usr/bin/env bash
# Установка бота на Ubuntu (Oracle Cloud Always Free)
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/emm-bot}"
SERVICE_NAME="emm-bot"

echo "==> Каталог: $APP_DIR"
cd "$APP_DIR"

if [[ ! -f bot.py ]]; then
  echo "Ошибка: в $APP_DIR нет bot.py. Сначала скопируйте проект сюда."
  exit 1
fi

if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env
    echo "Создан .env из .env.example — впишите BOT_TOKEN:"
    echo "  nano $APP_DIR/.env"
  else
    echo "Ошибка: нет .env и .env.example"
    exit 1
  fi
fi

echo "==> Пакеты"
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

echo "==> venv + зависимости"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "==> systemd"
SERVICE_SRC="$APP_DIR/deploy/emm-bot.service"
if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "Ошибка: нет $SERVICE_SRC"
  exit 1
fi

# Подставить текущего пользователя и путь
TMP_SERVICE="$(mktemp)"
sed \
  -e "s|User=ubuntu|User=$USER|g" \
  -e "s|/home/ubuntu/emm-bot|$APP_DIR|g" \
  "$SERVICE_SRC" > "$TMP_SERVICE"

sudo cp "$TMP_SERVICE" "/etc/systemd/system/${SERVICE_NAME}.service"
rm -f "$TMP_SERVICE"

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo
echo "==> Статус:"
sudo systemctl --no-pager --full status "$SERVICE_NAME" || true
echo
echo "Логи:   sudo journalctl -u $SERVICE_NAME -f"
echo "Стоп:   sudo systemctl stop $SERVICE_NAME"
echo "Старт:  sudo systemctl start $SERVICE_NAME"
echo
echo "Проверьте, что в .env заполнен BOT_TOKEN и TELEGRAM_PROXY пустой."
