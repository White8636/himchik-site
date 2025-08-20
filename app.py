from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import requests
import telebot  # импорт бота

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")
bot = telebot.TeleBot(TELEGRAM_TOKEN)


@app.route('/telegram', methods=['POST'])
def telegram_webhook():
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
            f"[{phone}](tel:{phone}) {name}\n"
            f"{entrance}-{floor}-{apartment} - {intercom}\n\n"
            f"{message}\n\n"
        )

        if services_text:
            text += f"{services_text}\n"

        send_text_to_telegram(text)

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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def send_photo_to_telegram(filepath):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(filepath, 'rb') as photo:
        payload = {'chat_id': TELEGRAM_CHAT_ID}
        files = {'photo': photo}
        requests.post(url, data=payload, files=files)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    bot.remove_webhook()
    bot.set_webhook(url='https://himchik.ru/telegram')

    app.run(debug=True)
