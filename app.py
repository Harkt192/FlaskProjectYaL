import flask

app = flask.Flask(__name__)


@app.route("/")
def hello():
    return flask.render_template("first_page.html", title="Welcome!")


@app.route("/choosesite")
def main():
    return flask.render_template("choose_sites.html", title="Choose site")


@app.route("/mysites")
def mysites():
    return flask.render_template("mysites.html", title="My sites")


@app.route("/feedback")
def feedback():
    return flask.render_template("feedback.html", title="Feedback")


@app.route("/about")
def about():
    return flask.render_template("about.html", title="About us")


# ---------
@app.route("/sites/<int:num>")
def site_pages(num):
    if num == 1:
        return flask.render_template("site1.html", title="First site")
    elif num == 2:
        return flask.render_template("site2.html", title="Second site")
    elif num == 3:
        return flask.render_template("site3.html", title="Third site")
    elif num == 4:
        return flask.render_template("site4.html", title="Fourth site")
    elif num == 5:
        return flask.render_template("site5.html", title="Fifth site")




if __name__ == '__main__':
    app.run()
