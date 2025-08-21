from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv
import telebot  # импорт бота
from telebot.formatting import escape_markdown
from telebot.apihelper import ApiException

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

load_dotenv()

def md2(text: str) -> str:
    """Escape text for Telegram MarkdownV2."""
    return escape_markdown(text or "", version=2)

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://example.com/telegram")
TELEGRAM_SECRET_TOKEN = os.getenv("TELEGRAM_SECRET_TOKEN", "your_secret_token")

if TELEGRAM_TOKEN == "your_telegram_token" or TELEGRAM_CHAT_ID == "your_chat_id":
    raise RuntimeError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не установлены")

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if secret_token != TELEGRAM_SECRET_TOKEN:
        return 'forbidden', 403

    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200


@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/trust')
def trust():
    return render_template('trust.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        entrance = request.form.get('entrance', '')
        floor = request.form.get('floor', '')
        apartment = request.form.get('apartment', '')
        intercom = request.form.get('intercom', '')
        message = request.form.get('message', '')
        consent = request.form.get('consent')
        files = request.files.getlist('photo')

        services = request.form.getlist('services')  # чекбоксы
        services_text = "\n".join(f"✔️ {s}" for s in services) if services else ''

        if not consent:
            return "Вы должны согласиться на обработку персональных данных.", 400

        # Кликабельный номер
    text = (
        f"[{phone}](tel:{phone}) {md2(name)}\n"
        f"{md2(entrance)}-{md2(floor)}-{md2(apartment)} - {md2(intercom)}\n\n"
        f"{md2(message)}\n\n"
     )

    if services:
        text += "\n".join(f"✔️ {md2(s)}" for s in services) + "\n"

        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode="MarkdownV2")

        for file in files[:10]:
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                send_photo_to_telegram(filepath)
                os.remove(filepath)

        return redirect('/')

    return render_template('form.html')

def send_text_to_telegram(text):
    try:
        escaped_text = escape_markdown(text, version=2)
        bot.send_message(TELEGRAM_CHAT_ID, escaped_text, parse_mode='MarkdownV2')
    except ApiException as e:
        app.logger.error(f"Error sending message: {e}")

def send_photo_to_telegram(filepath):
    try:
        with open(filepath, 'rb') as photo:
            bot.send_photo(TELEGRAM_CHAT_ID, photo)
    except (ApiException, OSError) as e:
        app.logger.error(f"Error sending photo: {e}")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL, secret_token=TELEGRAM_SECRET_TOKEN)

    app.run(debug=True)
