from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import time

# Инициализация приложения
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "clicks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Лимитер запросов
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["300 per hour", "50 per minute"]
)

MAX_CLICKS = 777777

# Модель базы данных
class Total(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

# Создание таблиц и начальной записи
with app.app_context():
    db.create_all()
    if not Total.query.first():
        db.session.add(Total(count=0))
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_click', methods=['POST'])
@limiter.limit("3/second")
def add_click():
    try:
        total = Total.query.first()
        
        if total.count >= MAX_CLICKS:
            return jsonify({'maxReached': True})
        
        # Защита от быстрых кликов
        now = time.time()
        last_click = getattr(request, 'last_click', 0)
        if now - last_click < 0.5:
            return jsonify({'error': 'Слишком быстро!'}), 429
        request.last_click = now
        
        # Обновление счетчика
        total.count += 1
        db.session.commit()
        
        return jsonify({
            'total': total.count,
            'maxReached': total.count >= MAX_CLICKS
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_clicks')
def get_clicks():
    total = Total.query.first()
    return jsonify({'total': total.count if total else 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
