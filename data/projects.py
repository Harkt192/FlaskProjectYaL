import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase  # для обмена данными sql
from werkzeug.security import generate_password_hash, check_password_hash  # пароли
import datetime
from flask_login import UserMixin


class Project(SqlAlchemyBase, UserMixin):
    __tablename__ = "projects"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)
    start_time = sqlalchemy.Column(sqlalchemy.DATETIME, default=datetime.datetime.now())