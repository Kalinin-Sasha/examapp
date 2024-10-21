from random import randint
from data.task import Task
from data.attachments import Attachment
from data.user_answers import UserAnswer
from data.db_session import create_session, global_init


class DBManager:
    EDGES = (1, 2555)

    def __init__(self, db_file):
        global_init(db_file)  # инициализировать БД (если ее нет, то создается новая по шаблону)
        self.session = create_session()  # начать сессию с базой данных

    def update_db(self, tasks):
        for task in tasks:
            new_task = Task()
            new_task.type = task[0]
            new_task.task = task[1] + '\n\nСписок ссылок:\n' + '\n'.join(task[2])
            new_task.solution = task[3] + '\n\n' + '\n'.join(task[4])
            new_task.answer = task[5]
            self.session.add(new_task)
            self.session.commit()
            for link in task[2]:
                attach = Attachment()
                attach.text_id = new_task.id
                attach.link = link
                self.session.add(attach)
                self.session.commit()
            for link in task[4]:
                attach = Attachment()
                attach.text_id = new_task.id
                attach.link = link
                self.session.add(attach)
                self.session.commit()

    def get_task(self, task_id):
        """Получить задание и ссылки к нему по его ID."""
        task = list(self.session.query(Task).filter(Task.id == task_id))[0]
        return [task.type, task.task, task.solution, task.answer] + \
               [list(map(lambda x: x.link,
                        self.session.query(Attachment).filter(Attachment.text_id == task_id)))]

    def get_tasks(self):
        """Получить все задания."""
        return list(map(lambda x: x.id, self.session.query(Task).all()))

    def get_tasks_by_type(self, task_type):
        """Отфильтровать задания по типу."""
        return list(map(lambda x: x.id, self.session.query(Task).filter(Task.type == task_type)))

    def get_type_by_task(self, task_id):
        """Определить тип задания по его ID."""
        return list(map(lambda x: x.type, self.session.query(Task).filter(Task.id == task_id)))[0]

    def get_random_task(self, task_type):
        """Вернуть id случайного задания данного типа."""
        ids = self.get_tasks_by_type(task_type)
        return randint(ids[0], ids[-1])

    def get_task_id_by_text(self, text):
        """Получить id задания по его тексту."""
        return list(self.session.query(Task).filter(Task.task == text))[0].id

    def save_user_answer(self, answer, task_id):
        """Сохранить ответ пользователя на задание task_id в базу данных."""
        user_answer = UserAnswer()
        user_answer.task_id = task_id
        user_answer.answer = answer
        self.session.add(user_answer)
        self.session.commit()

    def generate_variant(self):
        """Сгенерировать вариант из случайных заданий каждого типа."""
        indexes = []
        for i in range(1, 28):
            indexes.append(self.get_random_task(i))
        return list(map(lambda x: [x] + self.get_task(x), indexes))

    def close_session(self):
        """Завершить сессию с базой данных."""
        self.session.close()
