from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, PasswordField
from wtforms.validators import DataRequired, URL, Length

class add_desk_form(FlaskForm):
    deskname = StringField('Desk Name', validators = [DataRequired("You must enter a desk name, or you'll have a hard time finding it later."), Length(min = 1, max = 20, message = "The desk name must be between 1-20 characters.")])
    desc = TextAreaField('Desk Description')
    submit = SubmitField('Add Desk')

class edit_desk_form(FlaskForm):
    deskname = StringField('Desk Name', validators = [DataRequired("You must enter a desk name, or you'll have a hard time finding it later."), Length(min = 1, max = 20, message = "The desk name must be between 1-20 characters.")])
    desc = TextAreaField('Desk Description')
    submit = SubmitField('Edit Desk')
