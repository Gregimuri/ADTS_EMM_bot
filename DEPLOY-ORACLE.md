# Деплой на Oracle Cloud Always Free

Бот крутится на маленьком VPS (Ubuntu) как systemd-сервис, 24/7.  
Прокси для Telegram на зарубежном сервере обычно **не нужен**.

## 1. Аккаунт и инстанс

1. Зарегистрируйтесь: https://www.oracle.com/cloud/free/
2. Выберите **Home Region** внимательно (потом не сменить).
3. Console → **Compute** → **Instances** → **Create instance**
4. Рекомендуемые настройки Always Free:
   - Image: **Canonical Ubuntu 22.04** или **24.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere ARM) — 1 OCPU, 6 GB RAM достаточно
   - Если A1 недоступен в регионе: **VM.Standard.E2.1.Micro** (AMD)
5. Создайте/скачайте **SSH key** (`.key` / `.pem`) — без него не зайдёте.
6. В **VCN → Subnet → Security List** для SSH:
   - Ingress: TCP **22** с вашего IP (или временно `0.0.0.0/0`)
   - Для polling-бота входящие порты кроме SSH **не нужны**

Дождитесь статуса **Running**, скопируйте **Public IP**.

## 2. Копирование проекта на сервер

На своём ПК (PowerShell), из папки проекта:

```powershell
# путь к ключу и IP подставьте свои
$KEY = "$env:USERPROFILE\Downloads\ssh-key.key"
$IP  = "X.X.X.X"

# права на ключ (один раз)
icacls $KEY /inheritance:r
icacls $KEY /grant:r "$($env:USERNAME):(R)"

ssh -i $KEY "ubuntu@$IP" "mkdir -p ~/emm-bot"

scp -i $KEY `
  bot.py config.py sheets.py formatter.py proxy_detect.py requirements.txt .env.example `
  "ubuntu@${IP}:~/emm-bot/"

scp -i $KEY -r deploy "ubuntu@${IP}:~/emm-bot/"
```

Excel (`Список для Эдтех.xlsx`) копировать не обязательно — основной источник Google Sheets.

## 3. Токен и установка

```powershell
ssh -i $KEY "ubuntu@$IP"
```

На сервере:

```bash
cd ~/emm-bot
cp .env.example .env
nano .env
```

Впишите:

```env
BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_PROXY=
```

Сохраните (`Ctrl+O`, Enter, `Ctrl+X`), затем:

```bash
chmod +x deploy/setup.sh
./deploy/setup.sh
```

Проверка:

```bash
sudo systemctl status emm-bot
sudo journalctl -u emm-bot -f
```

В логах должны быть строки вроде `Telegram OK` и `Bot started`.  
Напишите боту в Telegram название ТТ.

## 4. Полезные команды

```bash
sudo systemctl restart emm-bot   # перезапуск
sudo systemctl stop emm-bot      # остановить
sudo journalctl -u emm-bot -n 100 --no-pager   # последние логи
```

Обновить код с ПК:

```powershell
scp -i $KEY bot.py formatter.py sheets.py config.py proxy_detect.py "ubuntu@${IP}:~/emm-bot/"
ssh -i $KEY "ubuntu@$IP" "sudo systemctl restart emm-bot"
```

## 5. Важно

- На сервере должен работать **только этот** экземпляр бота (локальный `bot.py` на ПК остановите).
- Если `getMe` / polling падают по сети — регион/файрвол провайдера; обычно на OCI всё ок без прокси.
- Always Free инстанс могут остановить при неоплате/проблемах с картой — следите за статусом в консоли.
- Токен не коммитьте в git; на сервере он только в `~/emm-bot/.env`.
