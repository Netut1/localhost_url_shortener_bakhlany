from flask import Flask, render_template, request, jsonify, redirect
from database import URLDatabase
from url_shortener import shorten_url, lengthen_url, get_base_url
import re

app = Flask(__name__)
db = URLDatabase()
BASE_SHORT_DOMAIN = "bakhlany.short"

def is_valid_url(url):
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_url():
    data = request.get_json()
    if not data:
        return jsonify({'result': 'Неверный формат запроса'}), 400

    long_url = data.get('long_url', '').strip()
    short_url_input = data.get('short_url', '').strip()
    max_records = data.get('max_records', 100)

    db.max_records = int(max_records)
    result = ""

    if long_url:
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url
        if not is_valid_url(long_url):
            return jsonify({'result': 'Ошибка: неверный формат URL'})

        base_url = get_base_url(long_url)
        existing_short = db.get_short_url(base_url)
        if existing_short:
            result = f"Существующий короткий URL: {existing_short}"
        else:
            new_short, base_url_used = shorten_url(long_url, BASE_SHORT_DOMAIN)
            success, message = db.add_url(base_url_used, new_short)
            if success:
                result = f"Создан короткий URL: {new_short}"
            else:
                result = f"Ошибка: {message}"

    elif short_url_input:
        if is_valid_url(short_url_input):
            lookup_url = short_url_input
        else:
            lookup_url = f"https://{BASE_SHORT_DOMAIN}/{short_url_input}"

        long = db.get_long_url(lookup_url)
        if long:
            result = f"Оригинальный URL: {long}"
        else:
            guessed = lengthen_url(lookup_url)
            if guessed:
                result = f"Предположительный URL: {guessed} (не подтверждён)"
            else:
                result = "Короткий URL не найден в базе данных"
    else:
        result = "Введите длинный или короткий URL"

    return jsonify({'result': result})

@app.route('/<path:short_path>')
def redirect_to_long(short_path):
    full_short_url = f"https://{BASE_SHORT_DOMAIN}/{short_path}"
    long_url = db.get_long_url(full_short_url)
    if long_url:
        return redirect(long_url)
    else:
        return "Короткий URL не найден", 404

@app.route('/clear', methods=['POST'])
def clear_database():
    success, message = db.clear_database()
    return jsonify({'result': message})

if __name__ == '__main__':
    print("=" * 50)
    print("Bakhlany URL Server запущен")
    print("http://localhost:4032")
    print("=" * 50)
    app.run(host='0.0.0.0', port=4032, debug=True)