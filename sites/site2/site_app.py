from flask import Flask, render_template, url_for, redirect, request, abort
from forms.forms import LoginForm, RegisterForm, PostForm, CommentForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
import datetime
import argparse

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment


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


site_app = Flask(__name__)
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


@site_app.route(f"/{USER_LOGIN}/")
def home():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).order_by(Post.date_posted.desc()).all()
    db_sess.close()
    return render_template('index.html',
                           posts=posts,
                           userlogin=USER_LOGIN,
                           title="Главная страница форума")

@site_app.route(f"/{USER_LOGIN}/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(f'/{USER_LOGIN}')
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/{USER_LOGIN}/login')
    return render_template('register.html',
                           title='Регистрация',
                           userlogin=USER_LOGIN,
                           form=form)

@site_app.route(f"/{USER_LOGIN}/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(f'/{USER_LOGIN}')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(f'/{USER_LOGIN}')
    return render_template('login.html',
                           title='Авторизация',
                           userlogin=USER_LOGIN,
                           form=form)

@site_app.route(f"/{USER_LOGIN}/logout")
def logout():
    logout_user()
    return redirect(f'/{USER_LOGIN}')

@site_app.route(f"/{USER_LOGIN}/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db_sess.add(post)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/{USER_LOGIN}/')
    return render_template('create_post.html',
                           title='Новый пост',
                           userlogin=USER_LOGIN,
                           form=form)

@site_app.route(f"/{USER_LOGIN}/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    try:
        db_sess = db_session.create_session()
        post = db_sess.query(Post).get(post_id)
        db_sess.close()
    except Exception:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db_sess.add(comment)
        db_sess.commit()
        db_sess.close()
        return redirect(url_for(f'/{USER_LOGIN}/post', post_id=post.id))
    return render_template('post.html', title=post.title, post=post, form=form)


db_session.global_init(PATH_TO_DB)
site_app.run(host=HOST, port=PORT)