from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField("Фамилия пользователя", validators=[DataRequired()])
    name = StringField("Имя пользователя", validators=[DataRequired()])
    login = StringField("Логин", validators=[DataRequired()])
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")

class LoginForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")