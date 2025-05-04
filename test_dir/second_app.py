from flask import Flask

second_app = Flask(__name__)

@second_app.route('/')
def home():
    return "<h1>Второй сайт работает! Закроется через 10 секунд.</h1>"

@second_app.route("/count/<int:num>")
def count_page(num):
    return f"<h1>{num} ** 3 = {num ** 3}</h1>"

if __name__ == '__main__':
    second_app.run(port=5000)  # Запускаем на другом порту