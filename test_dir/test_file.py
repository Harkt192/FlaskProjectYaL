import flask

app = flask.Flask(__name__)


@app.route("/")
def base():
    return flask.render_template("m1.html")


@app.route("/count/<int:num>")
def count_page(num):
    return f"""<h1 style="color: green"><b>{num ** 3}</b></h1>"""


def main():
    print("***Запуск 2 сайта***")
    app.run()


main()