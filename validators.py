from data import db_session
from data.__all_models import *
from wtforms.validators import ValidationError


def validate_email(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == field.data).first()
    if not user is None:
        raise ValidationError('User with this email already exists')