import flask
from data import db_session
from data.users import User
from data.users_files import User_files
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = "secret_key"
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

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
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


@app.route("/my_profile")
def profile():
    return flask.render_template("profile.html", title="Profile")


@app.route("/")
def hello():
    return flask.render_template("first_page.html", title="Welcome!")


@app.route("/choosesite")
def choose_site():
    return flask.render_template("choose_sites.html", title="Choose site")


@app.route("/mysites")
def mysites():
    return flask.render_template("mysites.html", title="My sites")


@app.route("/feedback")
def feedback():
    return flask.render_template("feedback.html", title="Feedback")


@app.route("/about")
def about():
    return flask.render_template("about.html", title="About us")


# ---------
@app.route("/sites/<int:num>")
def site_pages(num):
    if num == 1:
        return flask.render_template("site1.html", title="First site")
    elif num == 2:
        return flask.render_template("site2.html", title="Second site")
    elif num == 3:
        return flask.render_template("site3.html", title="Third site")
    elif num == 4:
        return flask.render_template("site4.html", title="Fourth site")
    elif num == 5:
        return flask.render_template("site5.html", title="Fifth site")


def main():
    db_session.global_init("db/database.db")
    app.run()


main()