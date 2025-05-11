from flask_restful import reqparse, abort, Api, Resource
from . import db_session
from .users import User
from flask import jsonify
from werkzeug.security import generate_password_hash

parser = reqparse.RequestParser()
parser.add_argument('login', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('name', required=True, type=str)
parser.add_argument('email', required=True, type=str)
parser.add_argument('hashed_password', required=True, type=str)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    if type(user_id) == int:
        user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(['surname', 'name', 'age']) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            login=args["login"],
            surname=args["surname"],
            name=args["name"],
            email = args["email"],
            hashed_password = generate_password_hash(args["hashed_password"])
        )
        session.add(user)
        session.commit()
        return jsonify(user.to_dict())


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_news_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)

        return jsonify({'user': user.to_dict(['surname', 'name', 'age'])})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})