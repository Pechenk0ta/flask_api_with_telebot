from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import jsonify
from flask import current_app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    tg_id = db.Column(db.String, unique=True, nullable=True)


    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username


    @staticmethod
    def register_user(upload):
        email = upload.get('email')
        password = upload.get('password')
        username = upload.get('username')
        if User.query.filter_by(username=username).first():
            return "A user with this username already exists"
        if  User.query.filter_by(email=email).first():
            return "A user with this email already exists"
        if (email and password and username):
            pass_hash = generate_password_hash(password)
            user = User(email=email, password=pass_hash, username=username)
        else:
            return "You missed an input field"
        db.session.add(user)
        db.session.commit()
        return ('Successfully')


    @staticmethod
    def login_user(payload):
        user = User.query.filter_by(username = payload.get('username')).first()
        if not user:
            return "Takogo usera ne suwestvuet"
        token = create_access_token(user.id)
        if not check_password_hash(user.password, payload.get('password')):
            return 'Credentials doesnt match', 400
        return jsonify(access_token=token)


    @staticmethod
    def change_tg_id(tg_id, id):
        user = User.query.filter_by(id = id).first()
        user.tg_id = tg_id
        db.session.commit()
