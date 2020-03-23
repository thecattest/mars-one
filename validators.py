from data import db_session
from data.__all_models import *
from wtforms.validators import ValidationError


def validate_email(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == field.data).first()
    if not user is None:
        raise ValidationError('User with this email already exists')


def validate_collaborators(form, field):
    session = db_session.create_session()
    ids = list(i for i in field.data.split(','))
    print(ids)
    if field.data:
        try:
            ids = list(int(i) for i in ids)
        except ValueError:
            raise ValidationError("Use only numbers and commas")
        db_ids = list(int(user.id) for user in session.query(User).all())
        if list(set(ids)) != ids:
            raise ValidationError("Every collaborator must be mentioned only once")
        if not set(ids).issubset(set(db_ids)):
            ids = set(ids).difference(set(db_ids))
            not_in_base = ', '.join(list(str(id) for id in ids))
            raise ValidationError("{} - not valid".format(not_in_base))