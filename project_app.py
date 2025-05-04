import flask
from data import db_session
from data.users import User
from data.users_files import User_files
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required

import webbrowser
import subprocess
import threading
import signal
import sys
import os

master_app = flask.Flask(__name__)

master_app.config["SECRET_KEY"] = "secret_key"
login_manager = LoginManager()
login_manager.init_app(master_app)

SERVER_PROCESS = None


def exit_cleanup(signum, frame):
    """Функция для корректного завершения второго сайта при выходе"""
    global SERVER_PROCESS
    if SERVER_PROCESS:
        print("\nЗавершаем работу сайта...")
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()
    sys.exit(0)


# Обработчик выключения программы
signal.signal(signal.SIGINT, exit_cleanup)  # Ctrl+C
signal.signal(signal.SIGTERM, exit_cleanup)  # Kill


def stop_site_in(delay):
    def shutdown():
        global SERVER_PROCESS
        if SERVER_PROCESS:
            SERVER_PROCESS.terminate()
            SERVER_PROCESS = None
            print("***САЙТ ВЫКЛЮЧЕН***")
    timer = threading.Timer(delay, shutdown)
    timer.start()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@master_app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Логин занят")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Уже существует пользователь с такой почтой")

        user = User(
            surname=form.surname.data,
            name=form.name.data,
            login=form.login.data,
            email=form.email.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        user_files = User_files(
            num_projects=0,
            dir_name=form.login.data,
            user_id=user.id
        )
        user_files.set_dir_name(form.login.data)
        db_sess.add(user_files)
        db_sess.commit()

        dir_name = db_sess.query(User_files).filter(User_files.user_id == user.id).first().dir_name
        os.mkdir(fr"./user_dirs/{dir_name}")

        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@master_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        dir_name = db_sess.query(User_files).filter(User_files.user_id == User.id).first().dir_name
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return flask.redirect("/")
        return flask.render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return flask.render_template('login.html', title='Авторизация', form=form)


@master_app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


@master_app.route("/my_profile")
def profile():
    return flask.render_template("profile.html", title="Profile")


@master_app.route("/")
def hello():
    return flask.render_template("first_page.html", title="Main page")


@master_app.route("/choosesite")
def choose_site():
    return flask.render_template("choose_sites.html", title="Choose site")


@master_app.route("/mysites")
def mysites():
    return flask.render_template("mysites.html", title="My sites")


@master_app.route("/feedback")
def feedback():
    return flask.render_template("feedback.html", title="Feedback")


@master_app.route("/about")
def about():
    return flask.render_template("about.html", title="About us")


# ---------
@master_app.route("/sites/<int:num>")
def site_pages(num):
    if num == 1:
        return flask.render_template("site1.html", title="First site")
    elif num == 2:
        return flask.render_template("site2.html", title="Second site")
    elif num == 3:
        return flask.render_template("site3.html", title="News site")
    elif num == 4:
        return flask.render_template("site4.html", title="Fourth site")
    elif num == 5:
        return flask.render_template("site5.html", title="Fifth site")


@master_app.route("/site/<string:action>/<int:num>")
def site_action_handler(action, num):
    global SERVER_PROCESS
    if action == "runsite":
        if not SERVER_PROCESS:
            path = fr"./sites/site{num}/site{num}_app.py"
            SERVER_PROCESS = subprocess.Popen(["python", path])
            stop_site_in(600)  # Принудительное выключение сайта через 10 минут.
        webbrowser.open("http://127.0.0.1:5000/", new=1)
    elif action == "closesite":
        if SERVER_PROCESS:
            os.kill(SERVER_PROCESS.pid, signal.SIGTERM)
        SERVER_PROCESS = None
    else:
        flask.abort(404)
    return flask.redirect(fr"/sites/{num}")


def main():
    db_session.global_init("db/database.db")
    master_app.run(host="127.0.0.1", port=8888)


main()
