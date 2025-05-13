from flask import Flask, render_template, url_for, redirect, request
from forms.forms import LoginForm, RegisterForm, PostForm, CommentForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import datetime
import argparse


def get_args() -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", nargs=1, type=int, dest="port")
    parser.add_argument("--user-login", nargs=1, type=str, dest="userlogin")
    parser.add_argument("--secret-key", nargs=1, type=str, dest="secret_key")
    parser.add_argument("--session-name", nargs=1, type=str, dest="session_name")

    args = parser.parse_args()
    port = args.port[0]
    userlogin = args.userlogin[0]
    secret_key = args.secret_key[0]
    session_name = args.session_name[0]
    return port, userlogin, secret_key, session_name


HOST = "127.0.0.1"
PORT, USER_LOGIN, SECRET_KEY, SESSION_NAME = get_args()


site_app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(site_app)
site_app.config["SECRET_KEY"] = f"{SECRET_KEY}_secret_key"
site_app.config["SESSION_COOKIE_NAME"] = f"{SESSION_NAME}_session"
site_app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///sites\site2\instance\forum.db'
db = SQLAlchemy(site_app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@site_app.route(f"/{USER_LOGIN}/")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
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
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
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
        user = User.query.filter_by(email=form.email.data).first()
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
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    return render_template('create_post.html',
                           title='Новый пост',
                           userlogin=USER_LOGIN,
                           form=form)

@site_app.route(f"/{USER_LOGIN}/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for(f'/{USER_LOGIN}/post', post_id=post.id))
    return render_template('post.html', title=post.title, post=post, form=form)


site_app.run(host=HOST, port=PORT)