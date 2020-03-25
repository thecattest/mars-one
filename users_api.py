from flask import Blueprint, jsonify, make_response, abort, request

from data import db_session
db_session.global_init("db/mars.sqlite")

from data.__all_models import *


users_blueprint = Blueprint("users_api", __name__,
                      template_folder="templates")


@users_blueprint.route("/api/users")
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return make_response(
        jsonify(
            {
                "users": [item.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                           'speciality', 'address', 'email')) for item in users]
            }
        ),
        200
    )


@users_blueprint.route("/api/users/<int:user_id>",  methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)
    return make_response(
        jsonify(
            {
                'user': user.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                           'speciality', 'address', 'email'))
            }
        ),
        200
    )


@users_blueprint.route("/api/users", methods=["POST"])
def create_user():
    if not request.json:
        return make_response({"error": "Empty request"}, 400)
    elif not all(key in request.json for key in
                 ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email']):
        abort(400)
    session = db_session.create_session()
    user = User()
    user.name = request.json["name"]
    user.surname = request.json["surname"]
    user.age = request.json["age"]
    user.position = request.json["position"]
    user.speciality = request.json["speciality"]
    user.address = request.json["address"]
    user.email = request.json["email"]

    session.add(user)
    session.commit()
    return make_response(
        jsonify({'success': 'ok',
                 'id': user.id}),
        200
    )


@users_blueprint.route("/api/users", methods=["PUT"])
def edit_user():
    session = db_session.create_session()
    keys = list(request.json.keys())
    if "id" not in keys:
        return make_response(jsonify({"error": "id must be specified"}), 400)
    user = session.query(User).get(request.json["id"])
    if not user:
        abort(404)
    if "surname" in keys:
        user.surname = request.json["surname"]
    if "name" in keys:
        user.name = request.json["name"]
    if "age" in keys:
        user.age = request.json["age"]
    if "position" in keys:
        user.position = request.json["position"]
    if "speciality" in keys:
        user.speciality = request.json["speciality"]
    if "address" in keys:
        user.address = request.json["address"]
    if "email" in keys:
        user.email = request.json["email"]
    session.commit()
    return make_response(jsonify({'success': 'OK'}), 200)


@users_blueprint.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)
    session.delete(user)
    session.commit()
    return make_response(jsonify({'success': 'OK'}), 200)