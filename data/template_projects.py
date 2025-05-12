import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase  # для обмена данными sql
from werkzeug.security import generate_password_hash, check_password_hash  # пароли
import datetime
from flask_login import UserMixin


class Template_project(SqlAlchemyBase, UserMixin):
    __tablename__ = "Template_projects"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    site_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    num_purchases = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    explanation = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def to_dict(self, params):
        dict_ = {"id": self.id,
                 "site_name": self.site_name,
                 "name": self.name,
                 "type": self.type,
                 "about": self.about,
                 "explanation": self.explanation,
                 "num_purchases": self.num_purchases}
        if params == "*":
            return dict_
        return_dict = {param: dict_[param] for param in params}
        return return_dict
