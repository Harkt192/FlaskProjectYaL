from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("main.html")

@app.route('/chat')
def main():
    return 'Страница с чатом'

if __name__ == '__main__':
    app.run(port=8000, host="127.0.0.1")
