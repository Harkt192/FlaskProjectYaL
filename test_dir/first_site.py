import flask
import subprocess
import webbrowser
import signal
import os
import sys
import threading


general_app = flask.Flask(__name__)
server_process = None


def cleanup_on_exit(signum, frame):
    """Функция для корректного завершения второго сайта при выходе"""
    global server_process
    if server_process:
        print("\nЗавершаем работу сайта...")
        server_process.terminate()
        server_process.wait()
    sys.exit(0)


# Обработчик выключения программы
signal.signal(signal.SIGINT, cleanup_on_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, cleanup_on_exit)  # kill


def stop_second_site_after(delay):
    """Отключает второй сайт через `delay` секунд"""
    def shutdown():
        global server_process
        if server_process:
            server_process.terminate()
            server_process = None
            print("Второй сайт отключён!")
    # Запускаем таймер
    timer = threading.Timer(delay, shutdown)
    timer.start()


@general_app.route("/")
def main_page():
    return flask.render_template("main.html")


@general_app.route("/start_site")
def run_site():
    global server_process
    if not server_process:
        server_process = subprocess.Popen(["python", "../sites/site3/site_app.py"])
        stop_second_site_after(10)
    webbrowser.open("http://127.0.0.1:5000/", new=1)
    return flask.redirect("/")

@general_app.route("/stop_site")
def stop_site():
    global server_process
    if server_process:
        os.kill(server_process.pid, signal.SIGTERM)
    server_process = None
    return flask.redirect("/")


def general_main():
    print("***Запуск 1 сайта***")
    general_app.run(host="127.0.0.1", port=8000)


general_main()
