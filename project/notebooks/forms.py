from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Length
from wtforms_validators import AlphaNumeric, ActiveUrl
from project.models import Notebooks
from wtforms.validators import ValidationError

class notebook_form(FlaskForm):
    title = StringField('Notebook title', validators = [DataRequired('Every notebook needs a title, please fill in that information!')])
    url = StringField('Unique URL for your notebook', validators = [DataRequired("You won't be able to share your notebook without a URL, please enter a URL."), AlphaNumeric('The URL can only contain letters and numbers. No punctuation please.')])
    desc = TextAreaField('Brief description of notebook')
    access_code = StringField("Enter an access code to make this notebook private (case sensitive)")



class add_notebook_form(notebook_form):
    cover_img = StringField("URL for a cover image, ideally 300px by 400px")
    submit = SubmitField('Create Notebook')

    def validate_url(self, field):
        if Notebooks.query.filter_by(url = field.data).first() is not None:
            raise ValidationError('You already have a notebook with this URL. Please try a different one.')

class edit_notebook_form(notebook_form):
    cover_img = StringField("URL for a cover image, ideally 300px by 400px", validators = [ActiveUrl("The profile image field must contain an active URL.")])
    submit = SubmitField('Edit Notebook')

class get_access_form(FlaskForm):
    access_code = StringField('Please Enter the Access Code', validators = [DataRequired("Please enter the access code.")])
    submit = SubmitField('Get Access')
