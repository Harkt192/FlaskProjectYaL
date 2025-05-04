import flask
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required
import os

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
                                   message="Уже существует пользователь с такой почтой")

        user = User(
            name=form.name.data,
            email=form.email.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
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
            login_user(user)
            return flask.redirect("/")
        return flask.render_template('login.html',
                               message="Неправильная почта или пароль",
                               form=form)
    return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


@app.route("/")
def hello():
    return flask.render_template("index.html", title="Main page")


@app.route("/count/<int:num>")
def counting(num):
    return flask.render_template("count.html", title="Counting", num=num)


def main():
    print("__name__:", __name__)
    if __name__ == "__main__":
        db_session.global_init("../sites/site1/databases/site_db.db")
    else:
        db_session.global_init("./sites/site1/databases/site_db.db")
    app.run(host="127.0.0.1", port=5000)


main()