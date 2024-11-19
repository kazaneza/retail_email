# blueprints/configurations/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

class ConfigurationForm(FlaskForm):
    name = StringField('Configuration Name', validators=[DataRequired()])
    instance = StringField('Instance', validators=[DataRequired()])
    database_name = StringField('Database Name', validators=[DataRequired()])
    authentication_method = SelectField(
        'Authentication Method',
        choices=[('SQL', 'SQL Authentication'), ('Windows', 'Windows Authentication')],
        validators=[DataRequired()]
    )
    username = StringField('Username')
    password = PasswordField('Password')
    table_name = StringField('Table Name', validators=[DataRequired()])
    submit = SubmitField('Save')
