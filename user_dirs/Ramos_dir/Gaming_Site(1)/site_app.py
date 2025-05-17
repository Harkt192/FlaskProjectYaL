from flask import Flask, render_template
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


site_app = Flask(__name__)
site_app.config["SECRET_KEY"] = f"{SECRET_KEY}_secret_key"
site_app.config["SESSION_COOKIE_NAME"] = f"{SESSION_NAME}_session"


@site_app.route(f"/{USER_LOGIN}/")
def home():
    return render_template('snake.html')


site_app.run(host=HOST, port=PORT)