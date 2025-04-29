import flask
import subprocess
import signal
import os


general_app = flask.Flask(__name__)
server_process = None


@general_app.route("/")
def main_page():
    return flask.render_template("main.html")


@general_app.route("/run_site")
def run_site():
    global server_process
    server_process = subprocess.Popen(["python", "test_file.py"])
    return flask.redirect("/")


@general_app.route("/stop_site")
def stop_site():
    global server_process
    os.kill(server_process.pid, signal.SIGTERM)
    return flask.redirect("/")


def general_main():
    print("***Запуск 1 сайта***")
    general_app.run(host="127.0.0.1", port=8000)


general_main()