from flask_restful import abort, Resource
from flask import jsonify
from data import db_session
from data.__all_models import User
from parsers import UserParser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))
            for item in users]})

    def post(self):
        args = UserParser.parse_args()
        session = db_session.create_session()
        user = User()
        user.surname = args["surname"]
        user.name = args["name"]
        user.age = args["age"]
        user.position = args["position"]
        user.speciality = args["speciality"]
        user.address = args["address"]
        user.email = args["email"]
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})