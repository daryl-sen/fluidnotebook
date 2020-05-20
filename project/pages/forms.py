from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError

class add_page_form(FlaskForm):
    heading = StringField('Page Heading', validators = [DataRequired("Please enter a heading for the page")])
    content = HiddenField('Content', validators = [DataRequired()])
    submit = SubmitField('Add Page')

class edit_page_form(FlaskForm):
    heading = StringField('Title of this page', validators = [DataRequired("Please enter a heading for the page")])
    content = HiddenField('Content', validators = [DataRequired()])
    submit = SubmitField('Edit Page')
