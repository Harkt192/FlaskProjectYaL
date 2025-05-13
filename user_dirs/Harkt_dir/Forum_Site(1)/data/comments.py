import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comment'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date_posted = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("post.id"))
    user = orm.relationship("User")
    post = orm.relationship("Post")