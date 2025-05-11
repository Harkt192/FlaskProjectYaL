import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase  # для обмена данными sql
from werkzeug.security import generate_password_hash, check_password_hash  # пароли
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "Users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    icon = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, default="user")
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_files = orm.relationship("User_files", back_populates="user")

    def to_dict(self, params):
        dict_ = {"id": self.id,
                 "surname": self.surname,
                 "name": self.name,
                 "login": self.login,
                 "email": self.email,
                 "hashed_password": self.hashed_password}
        return_dict = {param: dict_[param] for param in params}
        return return_dict

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)