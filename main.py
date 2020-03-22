from flask import Flask, render_template, request, redirect, make_response, session

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, EqualTo, ValidationError

from data import db_session
from data.__all_models import User, Jobs, Department

import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/mars.sqlite")


def validate_email(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == field.data).first()
    if not user is None:
        raise ValidationError('User with this email already exists')


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def main():
    app.run(port=8000)


def register_user(form):
    session = db_session.create_session()
    user = User()
    user.email = form.email.data
    user.name = form.name.data
    user.surname = form.surname.data
    user.age = form.age.data
    user.position = form.position.data
    user.speciality = form.speciality.data
    user.address = form.address.data
    user.set_password(form.password.data)
    try:
        session.add(user)
        session.commit()
    except Exception as error:
        log(error)
        return False, "Error was occured. Please, try again", "alert-danger"
    else:
        return True, "User was successfully registered!", "alert-success"


class RegisterForm(FlaskForm):
    email = EmailField('Your Email', validators=[InputRequired(), validate_email])
    password = PasswordField('Password', validators=[InputRequired(),
                                                   EqualTo('password_confirmation', message='Passwords must match')])
    password_confirmation = PasswordField('Repeat Password', validators=[InputRequired()])

    surname = StringField("Your Surname", validators=[InputRequired()])
    name = StringField("Your Name", validators=[InputRequired()])
    age = IntegerField("Your age", validators=[InputRequired()])

    position = StringField("Your Position", validators=[InputRequired()])
    speciality = StringField("Speciality", validators=[InputRequired()])

    address = StringField("Your address", validators=[InputRequired()])

    submit = SubmitField('Register')


@app.route("/")
@app.route("/index")
def index():
    session = db_session.create_session()
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
        ok, message, mes_class = register_user(form)
        messages.append((message, mes_class))
        if ok:
            return redirect('/register')
    return render_template("register.html", title="Register", form=form, messages=messages)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/session_test')
def session_test():
    if 'visits_count' in session:
        session['visits_count'] = session.get('visits_count') + 1
    else:
        session['visits_count'] = 1
    return f"Вы пришли на эту страницу {session['visits_count']} раз"


if __name__ == '__main__':
    main()