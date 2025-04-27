from .db_session import SqlAlchemyBase  # для обмена данными sql
import sqlalchemy
import sqlalchemy.orm as orm

# from werkzeug.security import generate_password_hash, check_password_hash  # пароли
from flask_login import UserMixin


class User_files(SqlAlchemyBase, UserMixin):
    __tablename__ = "Users_files"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    num_projects = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dir_name = sqlalchemy.Column(sqlalchemy.TEXT, unique=True, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Users.id"))
    user = orm.relationship("User")

    def set_dir_name(self, dirname):
        letters = list(dirname)
        self.dir_name = ""
        for letter in letters:
            self.dir_name += str(ord(letter))

    def check_dir_name(self, dirname):
        letters = list(dirname)
        dir_name = ""
        for letter in letters:
            dir_name += str(ord(letter))
        return dir_name == self.dir_name