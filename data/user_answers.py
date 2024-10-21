import sqlalchemy
from .db_session import SqlAlchemyBase


class UserAnswer(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tasks.id'))
    answer = sqlalchemy.Column(sqlalchemy.String)
