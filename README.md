# Himchik Site

Простое приложение на Flask для сайта клининговых услуг с интеграцией Telegram.

## Запуск локально

```bash
pip install -r requirements.txt
python app.py
```
Перед запуском создайте файл окружения и укажите свои ключи:

```bash
cp .env.example .env
# заполните TELEGRAM_TOKEN и TELEGRAM_CHAT_ID в .env
# заполните TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
# WEBHOOK_URL и TELEGRAM_SECRET_TOKEN в .env

## Деплой

Скрипт `deploy.sh` выполняет резервное копирование, обновление проекта и отправку уведомления в Telegram. Подробности в [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md).

## Безопасность

Не забудьте держать `TELEGRAM_TOKEN` в секрете. При необходимости можно использовать переменные окружения и файл `.env`, который добавлен в `.gitignore`.