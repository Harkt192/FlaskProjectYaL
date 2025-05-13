import flask

from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import argparse


def get_args() -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", nargs=1, type=int, dest="port")
    parser.add_argument("--user-login", nargs=1, type=str, dest="userlogin")
    parser.add_argument("--secret-key", nargs=1, type=str, dest="secret_key")
    parser.add_argument("--session-name", nargs=1, type=str, dest="session_name")
    parser.add_argument("--path-to-db", nargs=1, type=str, dest="path_to_db")

    args = parser.parse_args()
    port = args.port[0]
    userlogin = args.userlogin[0]
    secret_key = args.secret_key[0]
    session_name = args.session_name[0]
    path_to_db = args.path_to_db[0]
    return port, userlogin, secret_key, session_name, path_to_db


HOST = "127.0.0.1"
PORT, USER_LOGIN, SECRET_KEY, SESSION_NAME, PATH_TO_DB = get_args()


site_app = flask.Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(site_app)
site_app.config["SECRET_KEY"] = f"{SECRET_KEY}_secret_key"
site_app.config["SESSION_COOKIE_NAME"] = f"{SESSION_NAME}_session"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


@site_app.route(f'/{USER_LOGIN}/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(f"/{USER_LOGIN}/")


@site_app.route(f"/{USER_LOGIN}/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != 1))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    db_sess.close()
    return flask.render_template("index.html",
                                 userlogin=USER_LOGIN,
                                 news=news)


@site_app.route(f'/{USER_LOGIN}/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return flask.redirect(f"/{USER_LOGIN}/")
        return flask.render_template('login.html',
                                     message="Неправильный логин или пароль",
                                     userlogin=USER_LOGIN,
                                     form=form)
    return flask.render_template('login.html',
                                 title='Авторизация',
                                 userlogin=USER_LOGIN,
                                 form=form)


@site_app.route(f'/{USER_LOGIN}/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html',
                                         title='Регистрация',
                                         form=form,
                                         userlogin=USER_LOGIN,
                                         message="Пароли не совпадают")
        db_sess = db_session.create_session()
        sovp = db_sess.query(User).filter(User.email == form.email.data).first()
        if sovp:
            db_sess.close()
            return flask.render_template('register.html',
                                         title='Регистрация',
                                         form=form,
                                         userlogin=USER_LOGIN,
                                         message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return flask.redirect(f'/{USER_LOGIN}/login')
    return flask.render_template('register.html',
                                 title='Регистрация',
                                 userlogin=USER_LOGIN,
                                 form=form)


@site_app.route(f'/{USER_LOGIN}/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News(
            title=form.title.data,
            content=form.content.data,
            is_private=form.is_private.data,
            user_id=current_user.id
        )
        db_sess.add(news)
        db_sess.commit()
        db_sess.close()
        return flask.redirect(f'/{USER_LOGIN}/')
    return flask.render_template('news.html',
                                 title='Добавление новости',
                                 userlogin=USER_LOGIN,
                                 form=form)


@site_app.route(f'/{USER_LOGIN}/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if flask.request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        db_sess.close()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            flask.abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            db_sess.close()
            return flask.redirect(f'/{USER_LOGIN}/')
        else:
            db_sess.close()
            flask.abort(404)
    return flask.render_template('news.html',
                                 title='Редактирование новости',
                                 userlogin=USER_LOGIN,
                                 form=form)


def main():
    db_session.global_init(PATH_TO_DB)
    site_app.run(host=HOST, port=PORT)


main()
