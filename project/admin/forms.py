from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, PasswordField
from wtforms.validators import DataRequired, URL

class add_user(FlaskForm):
    username = StringField('Username')
    email = StringField('Email Address')
    password = PasswordField('Password')
    bio = TextAreaField('About Yourself')
    pic = StringField('Profile Picture URL')
    active_desk = IntegerField('Active Desk')
    submit = SubmitField('Add User')

class add_desk(FlaskForm):
    deskname = StringField('Desk Name')
    owner = IntegerField('Owner ID')
    desc = TextAreaField('Description')
    submit = SubmitField('Add Desk')

class add_notebook(FlaskForm):
    title = StringField('Notebook Title')
    desc = TextAreaField('Notebook Description')
    creation_date = StringField('Creation Date')
    last_update = StringField('Last Update')
    visibility = StringField('Visibility')
    access_code = StringField('Access Code')
    url = StringField('Unique URL')
    cover_img = StringField('Cover Image URL')
    owner = IntegerField('Owner ID')
    desk = IntegerField('Desk ID')
    submit = SubmitField('Add Notebook')

class add_page(FlaskForm):
    prior = IntegerField('Prior page')
    next = IntegerField('Next page')
    heading = StringField('Page Heading')
    content = TextAreaField('Page Content')
    last_update = StringField('Last Update')
    notebook = StringField('Notebook')
    author = StringField('Author')
    submit = SubmitField('Add Page')
