from flask import Flask, render_template, request, redirect, make_response, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
db_session.global_init("db/mars.sqlite")

from data.__all_models import *
from forms.__all_forms import *

import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def main():
    app.run(port=8000)


@app.route("/")
@app.route("/index")
def index():
    session = db_session.create_session()
    actions = session.query(Jobs).all()
    return render_template("actions.html",
                           actions=actions,
                           title="Список работ")


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


@app.route("/job", methods=["GET", "POST"])
@login_required
def add_job():
    form = JobForm()
    message = ""
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs()
        job.job = form.name.data
        job.work_size = form.hours.data
        job.collaborators = form.collaborators.data
        job.team_leader = form.team_leader.data
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
                           button="Add")


@app.route("/job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    form = JobForm()
    message = ""
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if job:
            if current_user.id != 1 and current_user.id != job.creator:
                abort(403)
            form.name.data = job.job
            form.team_leader.data = job.team_leader
            form.hours.data = job.work_size
            form.collaborators.data = job.collaborators
            form.finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if job:
            if current_user.id != 1 and current_user.id != job.creator:
                abort(403)
            job.job = form.name.data
            job.team_leader = form.team_leader.data
            job.work_size = form.hours.data
            job.collaborators  = form.collaborators.data
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
                           button="Edit")


@app.route("/delete_job/<int:job_id>", methods=["GET", "POST"])
@login_required
def delete_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        if current_user.id != 1 and current_user.id != job.creator:
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