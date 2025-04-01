import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jinyuz:password@localhost/shared_db?schema=promocode_service_schema")
if "?schema=" in DATABASE_URL:
    DATABASE_URL, schema = DATABASE_URL.split("?schema=")
else:
    schema = "public"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.before_request
def set_search_path():
    db.session.execute(f"SET search_path TO promocode_service_schema;")

class PromoCode(db.Model):
    __tablename__ = 'promocodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, nullable=False) 
    discount = db.Column(db.Float, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/promocode', methods=['POST'])
def create_promocode():
    data = request.get_json()
    new_code = PromoCode(
        name=data['name'],
        description=data.get('description'),
        creator_id=data['creator_id'],
        discount=data['discount'],
        code=data['code']
    )
    db.session.add(new_code)
    db.session.commit()
    return jsonify({"message": "PromoCode created"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5002)


