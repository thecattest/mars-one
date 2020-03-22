from flask import Flask, render_template, request

from data import db_session
from data.__all_models import User, Jobs, Department
from forms import *

import sqlalchemy
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/mars.sqlite")
session = db_session.create_session()


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')

def main():
    app.run()


def register_user(form):
    user = User()
    user.email = form.email.data
    user.name = form.name.data
    user.surname = form.surname.data
    user.age = form.age.data
    user.position = form.position.data
    user.speciality = form.speciality.data
    user.address = form.address.data
    user.set_password(form.password.data)
    # try:
    session.add(User)
    session.commit()
    # except Exception as error:
      #  log(error)
       # return "Error was occured. Please, try again", "alert-danger"
    # else:
    return "User was successfully registered!", "alert-success"


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
    form = RegisterForm()
    messages = []
    if form.validate_on_submit():
        message, mes_class = register_user(form)
        messages.append((message, mes_class))
    return render_template("register.html", title="Register", form=form, messages=messages)


if __name__ == '__main__':
    main()