import flask
from data import db_session
from data.users import User
from data.users_files import User_files
from data.projects import Project
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import webbrowser
import subprocess
import threading
import signal
import sqlite3
import zipfile
import shutil
import sys
import os

master_app = flask.Flask(__name__)

master_app.config["SECRET_KEY"] = "secret_key"
master_app.config["SESSION_COOKIE_NAME"] = "master_session"
login_manager = LoginManager()
login_manager.init_app(master_app)

ALL_PORTS = {port: "free" for port in range(1111, 10000)}
FREE_PORTS = [port for port in range(1111, 10000)]

### 8888 - основной порт ###
ALL_PORTS.pop(8887)
FREE_PORTS.remove(8887)


def get_available_port() -> int:
    global FREE_PORTS, ALL_PORTS
    if FREE_PORTS:
        port = FREE_PORTS[-1]
        FREE_PORTS = FREE_PORTS[:-1]
        ALL_PORTS[port] = "is-used"
        return port
    return -1


def make_free_port(port: int):
    global FREE_PORTS, ALL_PORTS
    print(f"ПОРТ {port} СВОБОДЕН")
    ALL_PORTS[port] = "free"
    FREE_PORTS.append(port)


SERVER_PROCESS = {
    "site1": None,
    "site2": None,
    "site3": None,
    "site4": None,
    "site5": None
}


def exit_cleanup(*args):
    """Функция для корректного завершения шаблонных сайтов при выходе"""
    global SERVER_PROCESS
    for name, data in SERVER_PROCESS.items():
        if data:
            port, process = data["port"], data["process"]
            make_free_port(port)
            kill_process(name)
            print(f"***ЗАВЕРШАЕМ РАБОТУ САЙТА: {name} ***")
    print("\nПРОВЕРКА ПРОЦЕССОВ:", SERVER_PROCESS)
    sys.exit(0)


# Обработчик выключения программы
signal.signal(signal.SIGINT, exit_cleanup)  # Ctrl+C
signal.signal(signal.SIGTERM, exit_cleanup)  # Kill


@login_manager.user_loader
def load_user(user_id):
    print("***main_app***", user_id)
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
            dir_name=form.login.data + "_dir",
            user_id=user.id
        )
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
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return flask.redirect("/")
        return flask.render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return flask.render_template('login.html', title='Авторизация', form=form)


@master_app.route('/user_logout')
@login_required
def logout():
    print(f"***{current_user.login.upper()}***")
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
    if current_user.is_authenticated:
        db_session.global_init(fr"user_dirs/{current_user.login}_dir/projects.db")
        db_sess = db_session.create_session()

        projects = db_sess.query(Project).all()
        db_session.global_init("db/database.db")
        return flask.render_template(
            "mysites.html",
            title="My sites",
            projects=projects,
            login=current_user.login
        )
    return flask.render_template(
            "mysites.html",
            title="My sites",
            projects=[],
            login=""
        )


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


def kill_process(name_project: str):
    global SERVER_PROCESS
    if name_project.isdigit():
        name_project = "site" + name_project
    # Выключение сайта
    if name_project in SERVER_PROCESS and SERVER_PROCESS[name_project]:
        make_free_port(SERVER_PROCESS[name_project]["port"])
        os.kill(SERVER_PROCESS[name_project]["process"].pid, signal.SIGTERM)

    SERVER_PROCESS[name_project] = None
    if name_project not in ["site1", "site2", "site3", "site4", "site5"]:
        SERVER_PROCESS.pop(name_project)


def stop_site_in(name_project: str, time=60):
    def shutdown():
        global SERVER_PROCESS
        kill_process(name_project)
        print(f"***САЙТ ВЫКЛЮЧЕН ПО ИСТЕЧЕНИЮ {time} СЕКУНД***")
    timer = threading.Timer(time, shutdown)
    timer.start()


@master_app.route("/site/<string:action>/<string:arg>")
def site_action_handler(action: str, arg: str):
    global SERVER_PROCESS
    if action == "runsite":
        if arg.isdigit():
            name_project = "site" + arg
            path = f"./sites/site{arg}/site_app.py"
        else:
            name_project = f"{current_user.login}_{arg}"
            path = f"./user_dirs/{current_user.login}_dir/{arg}/site_app.py"

        if name_project in SERVER_PROCESS and SERVER_PROCESS[name_project]:
            webbrowser.open(f"http://127.0.0.1:{available_port}/{current_user.login}_/", new=1)
        else:
            available_port = get_available_port()
            if available_port != -1:
                SERVER_PROCESS[name_project] = {
                    "process": subprocess.Popen([
                        "python",
                        path,
                        f"--port={available_port}",
                        f"--user-login={current_user.login}_"
                    ]),
                    "port": available_port,
                    "user": current_user.login + "_"
                }
                stop_site_in(arg, time=600)  # Принудительное выключение сайта через 10 минут.
                webbrowser.open(f"http://127.0.0.1:{available_port}/{current_user.login}_/", new=1)
            else:
                return flask.render_template("no_servers.html", title="Error")

    elif action == "closesite":
        if arg.isdigit():
            name_project = "site" + arg
        else:
            name_project = f"{current_user.login}_{arg}"
        kill_process(name_project)

    elif action == "buysite":
        arg = int(arg)
        con = sqlite3.connect(fr"user_dirs/{current_user.login}_dir/projects.db")
        cursor = con.cursor()


        names = [
            "Site_for_Selling", "Forum_Site", "News_Site", "Gaming_Site", "Blog_Site"
        ]
        abouts = [
            "Этот сайт предназначен для продажи чего-либо.",
            "Форум Сайт, на этом сайте пользователи смогут обсуждать любые вопросы.",
            "Новостной Сайт, на нем можно публиковать любые новости.",
            "Игровой Сайт, на нем можно сделать любую игру",
            "Сайт для блога, благодаря этому сайту вы сможете быть ближе к своей аудитории"
        ]
        name_ = names[arg - 1] + "(1)"
        about_ = abouts[arg - 1]
        k = 1
        project_names = cursor.execute(
            """
            SELECT name FROM projects 
            """
        ).fetchall()
        while name_ in project_names:
            k += 1
            name_ = names[arg - 1] + f"({k})"
        project = Project(
            name=name_,
            about=about_,
            type=names[arg - 1]
        )
        print(project)
        cursor.execute(
            f"""
            INSERT INTO projects
            VALUES {project}
            """
        )
        con.close()

        shutil.copytree(
            fr"sites/site{arg}",
            fr"user_dirs/{current_user.login}_dir/{name_}"
        )
        make_reserve_arc(
            fr"user_dirs/{current_user.login}_dir/{name_}",
            fr"user_dirs/{current_user.login}_dir/{name_}"
        )
        return flask.redirect("/mysites")
    else:
        flask.abort(404)
    if arg.isdigit():
        return flask.redirect(f"/sites/{arg}")
    else:
        return flask.redirect("/mysites")


def make_reserve_arc(source: str, dest: str):
    name = source.split("/")[-1]
    left_part = "/".join(source.split("/")[:-1])
    archive_name = f"{name}.zip"
    with zipfile.ZipFile(archive_name, "w") as new_zip:
        for root, dirs, files in os.walk(source):
            for file in files:
                path = os.path.join(root, file)
                new_zip.write(path, path.replace(left_part, ""))
    shutil.move(archive_name, dest)


def main():
    db_session.global_init("./db/database.db")
    master_app.run(host="127.0.0.1", port=8887)


main()
