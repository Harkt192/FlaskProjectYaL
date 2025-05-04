import webbrowser

import flask
import subprocess
import threading

first_app = flask.Flask(__name__)
second_site_process = None  # Здесь храним процесс второго сайта

# HTML с кнопкой
HTML = """
<h1>Главный сайт</h1>
<button style="margin-bottom: 1em;" onclick="window.location.href='/start_second_site'">
    Запустить второй сайт
</button>
<button onclick="window.location.href='/close_second_site'">
    Запустить второй сайт
</button>
"""

def stop_second_site_after(delay):
    """Отключает второй сайт через `delay` секунд"""
    def shutdown():
        global second_site_process
        if second_site_process:
            second_site_process.terminate()
            second_site_process = None
            print("Второй сайт отключён!")
    # Запускаем таймер
    timer = threading.Timer(delay, shutdown)
    timer.start()

@first_app.route('/')
def home():
    return flask.render_template_string(HTML)

@first_app.route('/start_second_site')
def start_second_site():
    global second_site_process
    if not second_site_process:
        # Запускаем второй сайт в отдельном процессе
        second_site_process = subprocess.Popen(["python", "../test_dir/second_app.py"])
        # Отключаем его через 20 секунд
        stop_second_site_after(20)
    webbrowser.open("http://127.0.0.1:5000/")
    return flask.redirect("/")


@first_app.route("/close_second_site")
def close_second_site():
    global second_site_process
    if second_site_process:
        second_site_process.terminate()
        second_site_process = None
        print("Второй сайт отключён!")
    return flask.redirect("/")


first_app.run(host="127.0.0.1", port=8000)