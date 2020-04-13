from flask import Flask, render_template, request, redirect, make_response, session, abort, jsonify
# from flask_ngrok import run_with_ngrok
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api

from data import db_session
db_session.global_init("db/mars.sqlite")

from data.__all_models import *
from forms.__all_forms import *

from jobs_api import jobs_blueprint
from users_api import users_blueprint

import users_resource
import jobs_resource

import datetime
import os
import random
import requests


app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.register_blueprint(jobs_blueprint)
    app.register_blueprint(users_blueprint)

    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:job_id>')
    api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')

    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
    # app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def get_coord(city):
    key = '40d1649f-0493-4b70-98ba-98533de7710b'
    link = 'http://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': key,
        'geocode': city,
        'format': 'json'
    }
    response = requests.get(link, params)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = toponym["Point"]["pos"]
        return ','.join(coords.split())
    else:
        print('Error during request')
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None


@app.route("/")
@app.route("/index")
def index():
    session = db_session.create_session()
    actions = session.query(Jobs).all()
    return render_template("actions.html",
                           actions=actions,
                           title="Works log")


@app.route("/departments_list")
def departments_list():
    session = db_session.create_session()
    all_departments = session.query(Department).all()
    return render_template("departments.html",
                           title="Departments log",
                           all_departments=all_departments)


@app.route("/register", methods=['GET', 'POST'])
def register():
    message = ""
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = random.choice(['Moscow', 'New York', 'London', 'Paris', 'Rome', 'Los-Angeles'])
        user.set_password(form.password.data)
        try:
            session.add(user)
            session.commit()
        except Exception as error:
            log(error)
            ok, message = False, "Error was occurred. Please, try again"
        else:
            ok, message = True, ""
        if ok:
            return redirect('/register')
    return render_template("register.html",
                           title="Register",
                           form=form,
                           message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html",
                               title='Log in',
                               message="Password or login is incorrect",
                               form=form)
    return render_template('login.html', title='Log in', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/users_show/<int:user_id>')
def user_nostalgy(user_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    response = requests.get(f'http://localhost:8000/api/v2/users/{user_id}').json()
    if not 'user' in response:
        return render_template("city_from.html", message='User not found')
    user = response['user']
    city = user['city_from']
    coords = get_coord(city)
    yandex_link = f'https://static-maps.yandex.ru/1.x/?ll={coords}&spn=0.26557,0.23619&l=map&size=400,400'
    return render_template("city_from.html",
                           user=user,
                           yandex_link=yandex_link)


@app.route("/department", methods=["GET", "POST"])
@login_required
def add_department():
    form = DepartmentForm()
    message = ""
    if form.validate_on_submit():
        session = db_session.create_session()
        department = Department()
        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        try:
            session.add(department)
            session.commit()
        except Exception as error:
            log(error)
            ok, message = False, "Error was occurred. Please, try again"
        else:
            ok, message = True, ""
        if ok:
            return redirect('/departments_list')
    return render_template("department_form.html", title="Adding a Department",
                           form=form,
                           message=message,
                           button="Add",
                           action="Adding")


@app.route("/department/<int:department_id>", methods=["GET", "POST"])
@login_required
def edit_department(department_id):
    form = DepartmentForm()
    message = ""
    if request.method == "GET":
        session = db_session.create_session()
        department = session.query(Department).filter(Department.id == department_id).first()
        if department:
            if current_user.id != 1 and current_user.id != department.chief:
                abort(403)
            form.title.data = department.title
            form.chief.data = department.chief
            form.members.data = department.members
            form.email.data = department.email
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        department = session.query(Department).filter(Department.id == department_id).first()
        if department:
            if current_user.id != 1 and current_user.id != department.chief:
                abort(403)
            department.title = form.title.data
            department.chief = form.chief.data
            department.members = form.members.data
            department.email = form.email.data
            session.commit()
            return redirect('/departments_list')
        else:
            abort(404)
    return render_template("department_form.html", title="Editing a Department",
                           form=form,
                           message=message,
                           button="Edit",
                           action="Editing")


@app.route("/delete_department/<int:department_id>", methods=["GET", "POST"])
@login_required
def delete_department(department_id):
    session = db_session.create_session()
    department = session.query(Department).filter(Department.id == department_id).first()
    if department:
        if current_user.id != 1 and current_user.id != department.chief:
            abort(403)
        session.delete(department)
        session.commit()
        return redirect("/departments_list")
    else:
        abort(404)


@app.route("/job", methods=["GET", "POST"])
@login_required
def add_job():
    form = JobForm()
    message = ""
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs()
        job.job = form.name.data
        job.team_leader = form.team_leader.data
        job.kind = form.kind.data
        job.work_size = form.hours.data
        job.collaborators = form.collaborators.data
        job.creator = current_user.id
        job.is_finished = form.finished.data
        if job.is_finished:
            job.end_date = datetime.datetime.now()
        try:
            session.add(job)
            session.commit()
        except Exception as error:
            log(error)
            ok, message = False, "Error was occurred. Please, try again"
        else:
            ok, message = True, ""
        if ok:
            return redirect('/')
    return render_template("job_form.html", title="Adding a Job",
                           form=form,
                           message=message,
                           button="Add",
                           action="Adding a new Job")


@app.route("/job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    form = JobForm()
    message = ""
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if job:
            if current_user.id != 1 and current_user.id != job.creator and current_user.id != job.team_leader:
                abort(403)
            form.name.data = job.job
            form.team_leader.data = job.team_leader
            form.kind.data = job.kind
            form.hours.data = job.work_size
            form.collaborators.data = job.collaborators
            form.finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if job:
            if current_user.id != 1 and current_user.id != job.creator and current_user.id != job.team_leader:
                abort(403)
            job.job = form.name.data
            job.team_leader = form.team_leader.data
            job.kind = form.kind.data
            job.work_size = form.hours.data
            job.collaborators = form.collaborators.data
            if job.is_finished:
                if not form.finished.data:
                    # было завершено, теперь - нет
                    job.end_date = None
                    job.is_finished = form.finished.data
            else:
                if form.finished.data:
                    job.end_date = datetime.datetime.now()
                    job.is_finished = form.finished.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template("job_form.html", title="Editing a Job",
                           form=form,
                           message=message,
                           button="Edit",
                           action="Editing")


@app.route("/delete_job/<int:job_id>", methods=["GET", "POST"])
@login_required
def delete_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        if current_user.id != 1 and current_user.id != job.creator and current_user.id != job.team_leader:
            abort(403)
        session.delete(job)
        session.commit()
        return redirect("/")
    else:
        abort(404)


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