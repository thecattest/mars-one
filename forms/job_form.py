import sys
sys.path.append("..")
from data.__all_models import User, Category
from data.db_session import create_session

from validators import validate_collaborators

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField, BooleanField
from wtforms.validators import DataRequired


def team_leader_query():
    session = create_session()
    users = session.query(User, "name", "surname", "id").all()
    choice = list((user[3], ' '.join(user[1:3])) for user in users)
    return choice


def category_query():
    session = create_session()
    categories = session.query(Category).all()
    choice = list((category.id, category.id) for category in categories)
    return choice


class JobForm(FlaskForm):
    name = StringField("Name of Job", validators=[DataRequired()])
    team_leader = SelectField("Team Leader", choices=team_leader_query(), coerce=int)
    hours = IntegerField("Work Hours", validators=[DataRequired()])
    kind = SelectField("Hazard category", choices=category_query(), coerce=int)
    collaborators = StringField("Collaborators", validators=[validate_collaborators])
    finished = BooleanField("Is finished")
    submit = SubmitField()