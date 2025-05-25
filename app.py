from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///clicks.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

@app.before_first_request
def init_db():
    db.create_all()
    if not Click.query.first():
        db.session.add(Click(count=0))
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_clicks')
def get_clicks():
    clicks = Click.query.first()
    return jsonify({'totalClicks': clicks.count})

@app.route('/add_click', methods=['POST'])
def add_click():
    clicks = Click.query.first()
    clicks.count += 1
    db.session.commit()
    return jsonify({'totalClicks': clicks.count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
