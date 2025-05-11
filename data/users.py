import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase  # для обмена данными sql
from werkzeug.security import generate_password_hash, check_password_hash  # пароли
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "Users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_files = orm.relationship("User_files", back_populates="user")

    def to_dict(self, params):
        dict_ = {"id": self.id,
                 "surname": self.surname,
                 "name": self.name,
                 "age": self.age,
                 "position": self.position,
                 "speciality": self.speciality,
                 "address": self.address,
                 "email": self.email,
                 "hashed_password": self.hashed_password,
                 "modified_date": self.modified_date}
        return_dict = {param: dict_[param] for param in params}
        return return_dict

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)