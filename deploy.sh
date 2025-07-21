#!/bin/bash

### ────────────────────────────────
### 🕓 1. Подготовка и переменные
### ────────────────────────────────

APP_DIR="/opt/himchik"
BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/himchik_backup_$TIMESTAMP.tar.gz"
LOG_FILE="$APP_DIR/deploy.log"
TELEGRAM_TOKEN="7665022364:AAHp7Zeey557c2waxfXfAVWTgXqE4qJt0C8"
TELEGRAM_CHAT_ID="404748283"

echo "🚀 [$TIMESTAMP] Начинаем деплой..." | tee -a "$LOG_FILE"

### ────────────────────────────────
### 💾 2. Резервное копирование
### ────────────────────────────────

echo "💾 Создание резервной копии..." | tee -a "$LOG_FILE"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_FILE" "$APP_DIR" --exclude "$BACKUP_DIR"
echo "✅ Бэкап сохранён: $BACKUP_FILE" | tee -a "$LOG_FILE"

# Оставить только 5 последних бэкапов
ls -1t "$BACKUP_DIR"/himchik_backup_*.tar.gz | tail -n +6 | xargs -r rm --

### ────────────────────────────────
### 🔄 3. Обновление из Git
### ────────────────────────────────

echo "🔄 Обновление проекта из Git..." | tee -a "$LOG_FILE"
cd "$APP_DIR" || exit 1
git pull origin main | tee -a "$LOG_FILE" || exit 1

### ────────────────────────────────
### 🧪 4. Проверка синтаксиса
### ────────────────────────────────

echo "🧪 Проверка синтаксиса Python..." | tee -a "$LOG_FILE"
python3 -m py_compile app.py || {
  echo "❌ Ошибка в коде. Откат." | tee -a "$LOG_FILE"
  exit 1
}

### ────────────────────────────────
### 🔁 5. Перезапуск сервиса
### ────────────────────────────────

echo "🔁 Перезапуск systemd-сервиса..." | tee -a "$LOG_FILE"
systemctl restart himchik

sleep 3
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000)

if [ "$STATUS" = "200" ]; then
    echo "✅ Сайт успешно отвечает (HTTP 200)." | tee -a "$LOG_FILE"
    STATUS_ICON="✅"
else
    echo "⚠️ Сайт не отвечает (HTTP $STATUS)." | tee -a "$LOG_FILE"
    STATUS_ICON="⚠️"
fi

### ────────────────────────────────
### 🔔 6. Telegram-уведомление
### ────────────────────────────────

# Получаем имя текущей ветки
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Формируем многострочный текст уведомления
read -r -d '' TEXT << EOM
🚀 *Himchik: Деплой завершён*
🕓 Время: $(date '+%Y-%m-%d %H:%M:%S')
💾 Бэкап: \`$(basename "$BACKUP_FILE")\`
🔁 Сайт: $( [ "$STATUS" = "200" ] && echo "✅ (HTTP $STATUS)" || echo "⚠️ (HTTP $STATUS)" )
📂 Ветка: \`$GIT_BRANCH\`
EOM

# Отправляем в Telegram
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
  -d chat_id="$TELEGRAM_CHAT_ID" \
  --data-urlencode "text=$TEXT" \
  -d parse_mode="Markdown"



### ────────────────────────────────
### 🏁 Завершение
### ────────────────────────────────

echo "🏁 Деплой завершён: $TIMESTAMP" | tee -a "$LOG_FILE"
