import flask
from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

site_app = flask.Flask(__name__)

site_app.config["SECRET_KEY"] = "secret_key"
login_manager = LoginManager()
login_manager.init_app(site_app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@site_app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


@site_app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != 1))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return flask.render_template("index.html", news=news)


@site_app.route('/login', methods=['GET', 'POST'])
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


@site_app.route('/register', methods=['GET', 'POST'])
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
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@site_app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return flask.redirect('/')
    return flask.render_template('news.html', title='Добавление новости',
                           form=form)


@site_app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if flask.request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
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
            return flask.redirect('/')
        else:
            flask.abort(404)
    return flask.render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


def main():
    print("__name__:", __name__)
    if __name__ == "__main__":
        db_session.global_init("./sites/site3/databases/blogs.db")
    else:
        db_session.global_init("../sites/site3/databases/blogs.db")
    site_app.run(host="127.0.0.1", port=5000)


main()
