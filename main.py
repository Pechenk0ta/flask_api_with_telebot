from flask import Flask, request
from db import db
from taskservice import Tasks
from Userservice import User
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import telebot
import threading
from jwt.exceptions import DecodeError
import jwt
from celery import Celery
import datetime
from datetime import timedelta

app = Flask(__name__)
app.config.from_object('config')
bot = telebot.TeleBot('6099114734:AAFSEh5JmeDXEt96HKiQmp5VrSCy8olDGmo')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
app.config.update(
    CELERY_INCLUDE=['tasks'],
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
db.init_app(app)
jwt_manager = JWTManager(app)
app_context = app.app_context()
app_context.push()
db.create_all()


def start_telegram_bot():
    bot.infinity_polling()


@app.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
    return User.register_user( payload)


@app.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    return User.login_user(payload)


@app.route('/create_task', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.create_task(user_id, payload)


@app.route('/task_by_user')
@jwt_required()
def task_by_user():
    user_id = get_jwt_identity()
    return Tasks.get_tasks_by_user_id(user_id)


@app.route('/change_status', methods=['POST'])
@jwt_required()
def change_status():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.change_status(user_id, payload)


@app.route('/change_content', methods = ['POST'])
@jwt_required()
def change_content():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.change_content(user_id, payload)


@app.route('/update_time', methods=['POST'])
@jwt_required()
def update_time_end():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.update_time_end(user_id, payload)


@app.route('/change_notify', methods=['POST'])
@jwt_required()
def change_notify():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.change_notify(user_id, payload)


@app.route('/delete_task', methods=['POST'])
@jwt_required()
def delete():
    user_id = get_jwt_identity()
    payload = request.get_json()
    return Tasks.delete_taks(user_id, payload)


@celery.task(name='check_task', run_every=timedelta(minutes=1))
def check_task():
    tasks_to_notify = Tasks.query.filter_by(notify=True).all()
    for t in tasks_to_notify:
        user_for_task = User.query.filter_by(id=t.user_id).first()
        if t.date_end.date() == datetime.date.today() and t.date_end.hour == datetime.datetime.now().hour + 1:
            bot.send_message(user_for_task.tg_id,f'Ваше задание {t.name} истекает в течение часа' )
        if (t.date_end < datetime.datetime.utcnow() and t.status != 'Prosrok'):
            t.status = 'Prosrok'
            db.session.commit()

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    with app.app_context():
        try:
            decoded_token = jwt.decode(message.text, options={"verify_signature": False})
            bot.send_message(message.chat.id, 'Токен записан')
            User.change_tg_id(tg_id=message.chat.id, id=decoded_token.get('sub'))
            db.session.commit()
        except DecodeError:
            bot.send_message(message.chat.id, "Неправильный токен")


if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.start()

    app.run()
