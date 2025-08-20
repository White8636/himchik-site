# 🚀 Деплой и восстановление проекта Himchik

Актуально на 2025-08-20 20:08:55

---

## 📦 Деплой проекта

### Запуск деплоя вручную:
```bash
cd /opt/himchik
./deploy.sh
```
### Переменные окружения
Перед запуском убедитесь, что заданы переменные с данными для Telegram:

```bash
export TELEGRAM_TOKEN="your_telegram_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export WEBHOOK_URL="https://example.com/telegram"
export TELEGRAM_SECRET_TOKEN="your_secret_token"
```

### Что делает `deploy.sh`:
1. ✅ Создаёт резервную копию в `/opt/backups`.
2. 🧹 Оставляет только 5 последних бэкапов.
3. 🔄 Обновляет проект из Git (`git pull` ветка `main`).
4. 🔍 Проверяет код на синтаксис (`py_compile`).
5. 🔁 Перезапускает сервис Gunicorn (`himchik.service`).
6. 📡 Проверяет сайт (ответ от `http://127.0.0.1:8000`).
7. 📬 Отправляет уведомление в Telegram.

---

## ♻️ Восстановление из бэкапа

1. Перейти в папку проекта:
```bash
cd /opt/himchik
```

2. Посмотреть список доступных бэкапов:
```bash
ls -lt /opt/backups
```

3. Распаковать нужный:
```bash
sudo tar -xzf /opt/backups/himchik_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

4. Перезапустить сервис:
```bash
sudo systemctl restart himchik
```

> ⚠️ Осторожно! Это полностью заменит содержимое `/opt/himchik` и восстановит `venv`, `app.py`, `templates`, `uploads` и т.д.

---

## 🧼 Полезные команды

### Логи:
```bash
journalctl -u himchik.service -e
cat /var/log/himchik/error.log
cat /var/log/himchik/access.log
```

### Тест Gunicorn вручную:
```bash
/opt/himchik/venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 app:app
```
