import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from datetime import datetime
from sqlalchemy import text
from database.database import engine, Base
Base.metadata.create_all(engine)  # Создаем таблицы при старте



app = Flask(__name__)

DATABASE_URL = "postgresql://jinyuz:password@soa_hws-shared_db-1/shared_db?options=-c search_path=user_service_schema"
schema = "user_service_schema"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

@app.before_request
def set_search_path():
    db.session.execute(text(f"SET search_path TO user_service_schema;"))
    db.session.commit() 

class User(db.Model):
    __tablename__ = 'users'  # Явное указание имени таблицы
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    login = fields.Str()
    email = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    date_of_birth = fields.Date()
    phone_number = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class RegistrationSchema(Schema):
    login = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    schema = RegistrationSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    if User.query.filter_by(login=data['login']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Login or email already exists'}), 400
    
    user = User(login=data['login'], password=data['password'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(login=data['login']).first()
    
    if not user or user.password != data['password']:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))

@app.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.date_of_birth = data.get('date_of_birth', user.date_of_birth)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.updated_at = datetime.utcnow()

    db.session.commit()

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user))

@app.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    return jsonify({"message": "Token is valid"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


