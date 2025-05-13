import flask
from data import db_session
from data.users import User
from data.users_files import User_files
from data.projects import Project
from data.template_projects import Template_project
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api, Resource
from data.sites_resources import TemplateSites_ListResource, TemplateSites_Resource, Sites_ListResourse

import webbrowser
import subprocess
import threading
import datetime
import signal
import sqlite3
import zipfile
import shutil
import sys
import os

master_app = flask.Flask(__name__)
api = Api(master_app)
master_app.config["SECRET_KEY"] = "secret_key"
master_app.config["SESSION_COOKIE_NAME"] = "master_session"
master_app.config['UPLOAD_FOLDER'] = 'static/uploads'
master_app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
login_manager = LoginManager()
login_manager.init_app(master_app)
api.add_resource(TemplateSites_ListResource, '/api/sites')
api.add_resource(TemplateSites_Resource, '/api/sites/<site_id>')
# api.add_resource(TemplateSites_ListResource, '/api/sites')

avatars_list = [
    'avatars/avatar1.png',
    'avatars/avatar2.png',
    'avatars/avatar3.png'
]


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
            port, process, user = data["port"], data["process"], data["user"]
            print(name, process)
            os.kill(process.pid, signal.SIGTERM)
            make_free_port(port)
            print(f"***ЗАВЕРШАЕМ РАБОТУ САЙТА: {name} ***")
    print("\nПРОВЕРКА ПРОЦЕССОВ:", SERVER_PROCESS)
    sys.exit(0)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in master_app.config['ALLOWED_EXTENSIONS']


# Обработчик выключения программы
signal.signal(signal.SIGINT, exit_cleanup)  # Ctrl+C
signal.signal(signal.SIGTERM, exit_cleanup)  # Kill


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


@master_app.route('/check-user')
def check_user():
    if current_user.is_authenticated:
        return flask.jsonify({'authenticated': True, 'login': current_user.login})
    return flask.jsonify({'authenticated': False})


def check_password(password: str) -> tuple:
    if password.isdigit():
        return False, "Пароль не может состоять только из цифр"
    if len(password) < 6 or len(password) > 50:
        return False, "Длина пароля должна быть в пределах 6-50 символов"
    nums = [str(i) for i in range(0, 10)]
    for num in nums:
        if num in password:
            break
    else:
        return False, "В пароле должны быть цифры"
    return True, None


def check_form(form: RegisterForm):
    check_result, check_message = check_password(form.password)
    if not check_result:
        return flask.render_template('register.html', title='Регистрация',
                                     form=form,
                                     message=check_message)
    if form.password.data != form.password_again.data:
        return flask.render_template('register.html', title='Регистрация',
                                     form=form,
                                     message="Пароли не совпадают")
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.login == form.login.data).first():
        return flask.render_template('register.html', title='Регистрация',
                                     form=form,
                                     message="Логин занят")
    if "site" in form.login:
        return flask.render_template('register.html', title='Регистрация',
                                     form=form,
                                     message="Ваш логин не может содержать site")
    if db_sess.query(User).filter(User.email == form.email.data).first():
        return flask.render_template('register.html', title='Регистрация',
                                     form=form,
                                     message="Уже существует пользователь с такой почтой")


@master_app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        check_form(form)

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
        db_sess.close()
        dir_name = db_sess.query(User_files).filter(User_files.user_id == user.id).first().dir_name
        os.mkdir(f"./user_dirs/{dir_name}")
        shutil.copy(os.path.join("db/", "projects.db"), f"./user_dirs/{dir_name}")
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@master_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
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
    logout_user()
    return flask.redirect("/")


@master_app.route("/my_profile")
@login_required
def profile():
    return flask.render_template("profile.html",
                               title="Профиль",
                               current_user=current_user)

@master_app.route('/choose_avatar', methods=['GET', 'POST'])
@login_required
def choose_avatar():
    if flask.request.method == 'POST':
        if 'custom_avatar' in flask.request.files:
            file = flask.request.files['custom_avatar']
            if file and allowed_file(file.filename):
                filename = f"user_{current_user.login}.{file.filename.rsplit('.', 1)[1].lower()}"
                file.save(os.path.join(master_app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = f"uploads/{filename}"
                db_sess = db_session.create_session()
                db_sess.merge(current_user)
                db_sess.commit()
                db_sess.close()
                return flask.redirect(flask.url_for('profile'))

        elif 'selected_avatar' in flask.request.form:
            selected = flask.request.form['selected_avatar']
            if selected in avatars_list:
                current_user.avatar = selected
                db_sess = db_session.create_session()
                db_sess.merge(current_user)
                db_sess.commit()
                db_sess.close()
                return flask.redirect(url_for('profile'))

    return flask.render_template('choose_avatar.html',
                               avatars=avatars_list,
                               current_user=current_user)


@master_app.route("/")
def hello():
    slides = [
        {"src": "images/mars_image_1.jpg",
         "alt": "Слайд 1",
         "caption": "Первый слайд"},
        {"src": "images/mars_image_2.png",
         "alt": "Слайд 2",
         "caption": "Второй слайд"},
        {"src": "images/mars_image_3.jpg",
         "alt": "Слайд 3",
         "caption": "Третий слайд"}
    ]
    return flask.render_template(
        "presentation.html",
        title="Основная Страница",
        presentation_images=slides
    )


@master_app.route("/sites")
def choose_site():
    return flask.render_template("sites.html", title="Сайты")


@master_app.route("/mysites")
def mysites():
    if current_user.is_authenticated:
        con = sqlite3.connect(fr"user_dirs/{current_user.login}_dir/projects.db")
        cursor = con.cursor()
        params = ["id", "name", "type", "about", "is_finished", "start_time"]
        user_projects = cursor.execute(
            f"""
            SELECT {", ".join(params)}
            FROM projects
            """
        ).fetchall()
        con.close()
        user_projects = list(map(
            lambda project: {par: project[params.index(par)] for par in params}, user_projects
        ))
        return flask.render_template(
            "mysites.html",
            title="My sites",
            projects=user_projects,
            login=current_user.login
        )
    return flask.render_template(
            "mysites.html",
            title="My sites",
            projects=[],
            login=""
        )


###----------------### Часть Макара
counter = 0
@master_app.route('/feedback', methods=['GET', 'POST'])
def chat():
    global counter
    messages = []

    if flask.request.method == 'POST':
        user_message = flask.request.form.get('user_message')

        if user_message:
            messages.append({'sender': 'user', 'text': user_message})
            if counter == 0:
                bot_response = f"Здравствуй! Чем могу быть полезен?"
            else:
                bot_response = f'Не могу помочь'
            messages.append({'sender': 'bot', 'text': bot_response})
        counter += 1

    return flask.render_template('feedback.html', messages=messages)


@master_app.route("/about")
def about():
    return flask.render_template("about.html", title="О нас")


all_temp = ["template_1", "template_2", "template_3"]
cart_list = ["template_1", "template_2"]

@master_app.route("/cart", methods=['GET', 'POST'])
def show_templates():
    global cart_list
    if flask.request.method == 'POST':
        action = flask.request.form.get('action')

        if action and action.startswith('remove_'):
            template_to_remove = action.replace('remove_', '')
            if template_to_remove in cart_list:
                cart_list.remove(template_to_remove)
            return flask.redirect('/cart')

        elif action == 'buy':
            return flask.redirect('/mysites')

        elif action == 'back':
            return flask.redirect('/choosesite')

    filtered_templates = [t for t in all_temp if t in cart_list]
    return flask.render_template("cart.html", templates=filtered_templates, cart_list_len=len(cart_list))
###----------------###


@master_app.route("/sites/<int:site_id>")
def site_pages(site_id):
    db_sess = db_session.create_session()
    project = db_sess.query(Template_project).get(site_id)
    site_name = project.site_name
    site_type = project.type
    db_sess.close()
    return flask.render_template(
        "site.html",
        title=site_type,
        site_name=site_name
    )


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
            path = f"./sites/site{arg}/"
        else:
            name_project = f"{current_user.login}_{arg}"
            path = f"./user_dirs/{current_user.login}_dir/{arg}/"

        if name_project in SERVER_PROCESS and SERVER_PROCESS[name_project]:
            webbrowser.open(f"http://127.0.0.1:{SERVER_PROCESS[name_project]["port"]}/{current_user.login}_/", new=1)
        else:
            available_port = get_available_port()
            print("***ПОРТ***",available_port)
            if available_port != -1:

                SERVER_PROCESS[name_project] = {
                    "process": subprocess.Popen([
                        "python",
                        path + "site_app.py",
                        f"--port={available_port}",
                        f"--user-login={current_user.login}_",
                        f"--secret-key={current_user.login[::-1] + str(available_port)}",
                        f"--session-name={(current_user.login + str(available_port))[::-1]}",
                        f"--path-to-db={path}db/database.db"
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


        db_sess = db_session.create_session()
        temp_project = db_sess.query(Template_project).get(arg)
        db_sess.close()

        con = sqlite3.connect(fr"user_dirs/{current_user.login}_dir/projects.db")
        cursor = con.cursor()

        names = [
            "News_Site", "Forum_Site", "Gaming_Site", "Site_for_Selling", "Blog_Site"
        ]
        project_name = names[arg - 1] + "(1)"
        project_about = temp_project.about
        project_type = temp_project.type
        project_is_finished = False
        # project_datetime = datetime.datetime.now().strftime("%d.%m.%Y %M:%H")
        project_datetime = datetime.datetime.now()

        project_names = cursor.execute(
            """
            SELECT name FROM projects 
            """
        ).fetchall()
        project_names = list(map(lambda x: x[0], project_names))

        k = 1
        while project_name in project_names:
            k += 1
            project_name = names[arg - 1] + f"({k})"
        project = Project(
            name=project_name,
            about=project_about,
            type=project_type,
            is_finished=project_is_finished,
            start_time=project_datetime
        )
        project_data = f"('{project.type}', '{project.name}', '{project.about}',\
{project.is_finished}, '{project.start_time}')"
        cursor.execute(
            f"""
            INSERT INTO projects (type, name, about, is_finished, start_time)
            VALUES {project_data}
            """
        )
        con.commit()
        con.close()

        shutil.copytree(
            fr"sites/site{arg}",
            fr"user_dirs/{current_user.login}_dir/{project_name}"
        )
        make_reserve_arc(
            fr"user_dirs/{current_user.login}_dir/{project_name}",
            fr"user_dirs/{current_user.login}_dir/{project_name}"
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
