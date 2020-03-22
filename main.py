from flask import Flask, render_template, request

from data import db_session
from data.__all_models import User, Jobs

import sqlalchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/mars.sqlite")
session = db_session.create_session()


def main():
    app.run()


def register_user(form):
    messages = []
    error = False

    email = form.get("email").strip()
    password = form.get("password").strip()
    password2 = form.get("password-repeat").strip()
    surname = form.get("surname").strip()
    name = form.get("name").strip()
    age = form.get("age").strip()
    position = form.get("position").strip()
    speciality = form.get("speciality").strip()
    address = form.get("address").strip()

    if password != password2:
        messages.append({"content": "Passwords do not match!", "class": "alert-danger"})
        error = True
    if not "@" in email:
        messages.append({"content": "Invalid email", "class": "alert-danger"})
        error = True
    if not error:
        user = User()
        user.email = email
        user.name = name
        user.surname = surname
        user.age = int(age)
        user.position = position
        user.speciality = speciality
        user.address = address
        user.set_password(password)
        try:
            session.add(user)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            messages.append({"content": "User with this email already exists", "class": "alert-danger"})
            session.rollback()
        else:
            messages.append({"content": "User was successfully registered!", "class": "alert-success"})

    return not error, messages, form




@app.route("/")
def index():
    actions = []
    for action in session.query(Jobs):
        actions.append({
            "id": action.id,
            "title": action.job,
            "leader": action.user.surname + ' ' + action.user.name,
            "duration": action.work_size,
            "collaborators": action.collaborators,
            "finished": action.is_finished
        })
    return render_template("actions.html", actions=actions, title="Список работ")


@app.route("/register", methods=['GET', 'POST'])
def register():
    params = {
        "title": "Register",
        "form": 0
    }
    if request.method == "GET":
        return render_template("register.html", **params)
    elif request.method == "POST":
        ok, messages, form = register_user(request.form)
        params["messages"] = messages
        if ok:
            params["form"] = form
        return render_template("register.html", **params)


if __name__ == '__main__':
    main()