import flask, sys
import subprocess


app = flask.Flask(__name__)


@app.route("/")
def base_page():
    return flask.render_template("base.html")

@app.route("/count/<int:num>")
def count_page(num):
    return flask.render_template("count.html", num=num)


@app.route("/shutdown")
def shutdown():
    subprocess.run("shutdown -h 0", shell=True, check=True)
    return "Shutting down!"


def main():
    app.run()



main()