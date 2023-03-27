from task import Tasks
from db import db
import datetime


class TaskService:











    def find_by_filter(self,user_id, filter):
        res = []
        for task in Tasks.query.filter_by(user_id=user_id):
            if (filter in task.name or filter in task.content
                    or filter in task.status):
                res.append(task)
        if res:
            return res
        else:
            return "Заданий по данному фильтру не было найдено"


    