import sys
sys.path.append("..")
from data.users import User
from data.db_session import create_session

from validators import validate_collaborators

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


def team_leader_query():
    session = create_session()
    users = session.query(User, "name", "surname", "id").all()
    choice = list((user[3], ' '.join(user[1:3])) for user in users)
    return choice


class DepartmentForm(FlaskForm):
    title = StringField("Title of Department", validators=[DataRequired()])
    chief = SelectField("Chief", choices=team_leader_query(), coerce=int)
    email = EmailField("Department Email", validators=[DataRequired()])
    members = StringField("Members", validators=[validate_collaborators])
    submit = SubmitField()