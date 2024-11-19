# blueprints/customers/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class CustomerForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Save')
