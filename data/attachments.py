import sqlalchemy
from .db_session import SqlAlchemyBase


class Attachment(SqlAlchemyBase):
    __tablename__ = 'attachments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tasks.id'))
    link = sqlalchemy.Column(sqlalchemy.String)
