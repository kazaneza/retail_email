# blueprints/customers/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class CustomerForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[('1', 'Not Yet'), ('2', 'Sent'), ('3', 'Failed')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Save')
