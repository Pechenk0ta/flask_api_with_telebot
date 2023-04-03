import datetime
from flask import jsonify
from db import db

class Tasks(db.Model):
    def __init__(self, name, content,  date_end,  user_id):
        self.name = name
        self.content = content
        self.date_end = date_end
        self.user_id = user_id


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String, nullable=False, default='IN_Work')
    date_start = db.Column(db.DateTime, default= datetime.datetime.utcnow)
    date_end = db.Column(db.DateTime)
    notify = db.Column(db.Boolean, default=False)


    @staticmethod
    def create_task(user_id, upload):
        task = Tasks(name=upload.get('name'), content=upload.get('content'), user_id=user_id,
                         date_end=(datetime.datetime.utcnow() + datetime.timedelta(hours=upload.get('date_end'))))
        db.session.add(task)
        db.session.commit()
        return ("Succesfully")


    @staticmethod
    def get_tasks_by_user_id(user_id):
        res = []
        tasks = Tasks.query.filter_by(user_id=user_id).all()
        for task in tasks:
            q ={
                'task_id':task.id,
                'task_name':task.name,
                'task_content':task.content,
                'status':task.status,
                'date_end':task.date_end
            }
            res.append(q)
        return jsonify(res)


    @staticmethod
    def change_status(user_id, upload):
        t = Tasks.query.filter_by(id=upload.get('id')).first()
        if t.user_id == user_id :
            t.status = upload.get('new_status')
            db.session.commit()
            return "Changes have been recorded"
        else:
            return "you do not have enough rights to change this data"


    @staticmethod
    def change_content(user_id, upload):
        t = Tasks.query.filter_by(id=upload.get('id')).first()
        if t.user_id == user_id:
            t.content = upload.get('content')
            db.session.commit()
            return "Changes have been recorded"
        else:
            return "you do not have enough rights to change this data"


    @staticmethod
    def update_time_end(user_id, upload):
        t = Tasks.query.filter_by(id=id).first()
        if t.user_id == user_id:
            t.time_end = datetime.utcnow + datetime.timedelta(hours=upload.get('date_end'))
            db.session.commit()
            return "Changes have been recorded"
        else:
            return "you do not have enough rights to change this data"


    @staticmethod
    def change_notify(user_id, upload):
        t = Tasks.query.filter_by(id=upload.get('id')).first()
        if t.user_id == user_id:
            if t.notify:
                t.notify = False
            else:
                t.notify = True
            db.session.commit()
        else:
            return "you do not have enough rights to change this data"


    @staticmethod
    def delete_taks(user_id, upload):
        t = Tasks.query.filter_by(id=upload.get('id')).first()
        if t.user_id == user_id:
            Tasks.query.filter_by(id=upload.get('id')).delete()
            db.session.commit()
            return "Data deleted"
        else:
            return "you do not have enough rights to change this data"


    @staticmethod
    def find_by_filter(user_id,upload):
        res = []
        for task in Tasks.query.filter_by(user_id=user_id):
            if (upload.get('filter') in task.name or upload.get('filter') in task.content
                    or upload.get('filter') in task.status):
                res.append(task)
        if res:
            return jsonify(res)
        else:
            return "Заданий по данному фильтру не было найдено"