from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, EqualTo, ValidationError

from data import db_session
from data.__all_models import User


def validate_email(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == field.data).first()
    if not user is None:
        raise ValidationError('User with this email already exists')


class RegisterForm(FlaskForm):
    email = EmailField('Your Email', validators=[InputRequired(), ]) # validate_email])
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