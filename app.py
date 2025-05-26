from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import time

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "clicks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MAX_CLICKS = 777777

class Total(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    if not Total.query.first():
        db.session.add(Total(count=0))
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_click', methods=['POST'])
def add_click():
    try:
        total = Total.query.first()
        
        if total.count >= MAX_CLICKS:
            return jsonify({'maxReached': True})
        
        # Оптимизированное обновление
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
    app.run(host='0.0.0.0', port=5000, threaded=True)  # Включена многопоточность
