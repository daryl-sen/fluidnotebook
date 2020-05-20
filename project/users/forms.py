from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField, TextField, TextAreaField, SubmitField, HiddenField, DateTimeField, RadioField, IntegerField)
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms_validators import AlphaNumeric, Integer, ActiveUrl
from wtforms.validators import ValidationError
from project.models import Users

class registration_form(FlaskForm):
    email = StringField('Email Address', validators = [DataRequired(), Email('You did not enter a proper format for your email address')])
    username = StringField('Username', validators = [DataRequired("You must enter a username, otherwise you won't be able to log in."), Length(min = 4, max = 20, message="Your username must be between 4-20 characters"), AlphaNumeric('Your username can only contain letter (A-Z, a-z) or numbers (0-9).')])
    password = PasswordField('Password', validators = [DataRequired("You can't leave your password blank, how will you log in?"), Length(min = 8, max = 50, message="Your password must be between 8-50 characters"), EqualTo('password_cfm', message = "The passwords entered below must match. Let's not get you locked out of your account for a typo!")])
    password_cfm = PasswordField('Confirm Password', validators = [DataRequired('You must confirm your password below. Sometimes people make a typo and get locked out of their account.')])
    submit = SubmitField('Agree and Register')

    def validate_username(self, field):
        def eval_name(name):
            blacklist = [
                # misleading
                'admin',
                'staff',
                'fluid',
                'webmaster',
                'administrator',
                # bad words
                'cunt',
                'fuck',
                'bitch'
                ]
            if any([banned in name for banned in blacklist]):
                return True
            else:
                return False

        if Users.query.filter_by(username = field.data).first() is not None or eval_name(field.data):
            raise ValidationError('This username is already in use, or it contains a banned word.')

    def validate_email(self, field):
        print(field.data)
        if Users.query.filter_by(email = field.data).first() is not None:

            raise ValidationError('This email address is already in use. Perhaps you already have an account?')




class login_form(FlaskForm):
    username = StringField('Username', validators = [DataRequired("You didn't fill in your username. Technology is advanced but not that advanced yet. Ack.")])
    password = PasswordField('Password', validators = [DataRequired("You didn't fill in your password. That's kinda important for logging in.")])
    submit = SubmitField('Log In')

class email_login_form(FlaskForm):
    email = StringField('Email Address', validators = [DataRequired("You didn't fill in your email address.")])
    password = PasswordField('Password', validators = [DataRequired("You didn't fill in your password. That's kinda important for logging in.")])
    submit = SubmitField('Log In With Email')


class changePassword_form(FlaskForm):
    current_pw = PasswordField('Current Password', validators = [DataRequired('Your must enter your current password.')])
    new_pw = PasswordField('New Password', validators = [DataRequired(), EqualTo('cfm_pw', message = "Your new passwords must match, or you'll have lots of trouble logging in later.")])
    cfm_pw = PasswordField('Confirm New Password', validators = [DataRequired("Please confirm your password.")])
    submit = SubmitField('Change Password')

class report_form(FlaskForm):
    type = SelectField('Type of Report', choices=[('BUG', 'Bug Report'), ('ABUSE', 'User Abuse Report'), ('DMCA', 'DMCA Takedown Request')], validators = [DataRequired()])
    title = StringField('Title of Report', validators = [DataRequired("Please enter a title so I can respond to this quickly.")])
    url = StringField('Where did this occur? Please provide a URL.', validators = [DataRequired('The url is required.')])
    content = TextAreaField('Detailed Description', validators = [DataRequired("You're gonna have to describe the problem, pretty please. All fields in this form are required.")])
    submit = SubmitField('Submit Report')

class preferences_form(FlaskForm):
    timezone = SelectField('Your Timezone', choices = [
        ('Etc/GMT+12', 'UTC-12 (US Baker Island)'),
        ('Etc/GMT+11', 'UTC-11 (American Samoa)'),
        ('Etc/GMT+10', 'UTC-10 (Honolulu)'),
        ('Etc/GMT+9', 'UTC-9 (Anchorage)'),
        ('Etc/GMT+8', 'UTC-8 (Pacific Time Zone - Vancouver, Los Angeles)'),
        ('Etc/GMT+7', 'UTC-7 (Calgary, Phoenix)'),
        ('Etc/GMT+6', 'UTC-6 (Winnipeg, Mexico City)'),
        ('Etc/GMT+5', 'UTC-5 (Toronto, New York)'),
        ('Etc/GMT+4', 'UTC-4 (Halifax, Santiago)'),
        ('Etc/GMT+3', 'UTC-3 (Buenos Aires, Montevideo)'),
        ('Etc/GMT+2', 'UTC-2 (Brazil, United Kingdom)'),
        ('Etc/GMT+1', 'UTC-1 (Denmark, Portugal)'),
        ('Etc/GMT0', 'UTC (London)'),
        ('Etc/GMT-1', 'UTC+1 (Berlin, Rome, Paris)'),
        ('Etc/GMT-2', 'UTC+2 (Cairo, Jerusalem)'),
        ('Etc/GMT-3', 'UTC+3 (Moscow, Istanbul, Baghdad)'),
        ('Etc/GMT-4', 'UTC+4 (Dubai, Baku)'),
        ('Etc/GMT-5', 'UTC+5 (Karachi)'),
        ('Etc/GMT-6', 'UTC+6 (Dhaka)'),
        ('Etc/GMT-7', 'UTC+7 (Jakarta, Ho Chi Mingh City, Bangkok)'),
        ('Etc/GMT-8', 'UTC+8 (Shanghai, Taipei, Singapore)'),
        ('Etc/GMT-9', 'UTC+9 (Tokyo, Seoul)'),
        ('Etc/GMT-10', 'UTC+10 (Sydney)'),
        ('Etc/GMT-11', 'UTC+11 (Australia)'),
        ('Etc/GMT-12', 'UTC+12 (Auckland)')
        ])
    night_time_on = IntegerField('Night Mode onset time (as a number, 8 PM = 20, 6 AM = 6)')
    night_time_off = IntegerField('Night Mode off time (as a number, 8 PM = 20, 6 AM = 6)')
    night_mode_type = RadioField('Night Mode type', choices = [
        ('dark', 'Dark'),
        ('black', 'Pure Black'),
        ('day', 'No nightmode'),
        ])

    font_size = SelectField('Font size', choices = [
        ('12', 'Extra Small'),
        ('15', 'Small'),
        ('18', 'Medium'),
        ('21', 'Large'),
        ('24', 'Extra Large'),
        ])
    coding_addon = BooleanField('Coding Addon')
    hyperlinks_addon = BooleanField('Hyperlinks Addon')
    colors_addon = BooleanField('Colors Addon')
    submit = SubmitField('Apply Changes')

class profile_form(FlaskForm):
    bio = TextAreaField('Short Biography', validators = [Length(min = 0, max = 1000)])
    email = TextField('Email Address', validators = [Email('Your email address is not in a valid format.'), DataRequired("Your email address is required for password recovery.")])
    pic = TextField('Profile Picture URL', validators = [ActiveUrl('The profile image field must contain an active URL.')])
    submit = SubmitField('Apply Changes')

class pw_reset_request_form(FlaskForm):
    email = TextField('Email Address', validators = [Email('Your email address is not in a valid format.'), DataRequired("Your email address is required for password recovery.")])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if Users.query.filter_by(email = field.data).first() is None:
            raise ValidationError('There is no account associated with this email address. Would you like to sign up instead?')

class pw_reset_form(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired("You can't leave your password blank, how will you log in?"), Length(min = 8, max = 50, message="Your password must be between 8-50 characters"), EqualTo('password_cfm', message = "The passwords entered below must match. Let's not get you locked out of your account for a typo!")])
    password_cfm = PasswordField('Confirm Password', validators = [DataRequired('You must confirm your password below. Sometimes people make a typo and get locked out of their account.')])
    submit = SubmitField('Set New Password')
