from project import db, login_manager, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# for password reset
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), index = True)
    email = db.Column(db.String(200), index = True)
    password = db.Column(db.String(200))
    bio = db.Column(db.Text)
    pic = db.Column(db.String(200))
    role = db.Column(db.String(200))
    active_desk = db.Column(db.Integer)
    desks = db.relationship('Desks', backref = "associated_owner", lazy = "dynamic")
    notebooks = db.relationship('Notebooks', backref = "associated_user", lazy = "dynamic")
    pages = db.relationship('Pages', backref = "associated_author", lazy = "dynamic")
    preferences = db.relationship('Preferences', backref = "associated_user", uselist = False)

    def __init__(self, username, email, password, bio, pic, active_desk):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.bio = bio
        self.pic = pic
        self.role = "learner"
        self.active_desk = active_desk

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expiry = 1800):
        s = Serializer(app.config['SECRET_KEY'], expiry)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)


desks_to_notebooks = db.Table('desks_to_notebooks',
    db.Column('desk_id', db.Integer, db.ForeignKey('desks.id')),
    db.Column('notebook_id', db.Integer, db.ForeignKey('notebooks.id'))
    )


class Desks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    deskname = db.Column(db.String(200))
    desc = db.Column(db.Text)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), index = True)
    notebooks = db.relationship('Notebooks', secondary = desks_to_notebooks, backref = db.backref('associated_desks'), lazy = "dynamic")

    def __init__(self, deskname, desc, owner):
        self.deskname = deskname
        self.desc = desc
        self.owner = owner


class Notebooks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    desc = db.Column(db.Text)
    creation_date = db.Column(db.String(200))
    last_update = db.Column(db.String(200))
    visibility = db.Column(db.String(200))
    access_code = db.Column(db.String(200))
    url = db.Column(db.String(200), index = True)
    cover_img = db.Column(db.String(200))
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), index = True)
    pages = db.relationship('Pages', backref="containing_notebook", lazy="dynamic")

    def __init__(self, title, desc, creation_date, last_update, visibility, access_code, url, cover_img, owner):
        self.title = title
        self.desc = desc
        self.creation_date = creation_date
        self.last_update = last_update
        self.visibility = visibility
        self.access_code = access_code
        self.url = url
        self.cover_img = cover_img
        self.owner = owner



class Pages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    prior = db.Column(db.Integer)
    next = db.Column(db.Integer)
    heading = db.Column(db.String(200))
    content = db.Column(db.Text)
    last_update = db.Column(db.String(200))
    notebook = db.Column(db.Integer, db.ForeignKey('notebooks.id'), index = True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), index = True)

    def __init__(self, prior, next, heading, content, last_update, notebook, author):
        self.prior = prior
        self.next = next
        self.heading = heading
        self.content = content
        self.last_update = last_update
        self.notebook = notebook
        self.author = author

class Reports(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(200), index = True)
    url = db.Column(db.String(200))
    content = db.Column(db.Text)
    user = db.Column(db.String(200))
    date = db.Column(db.String(20))

    def __init__(self, type, url, content, user, date):
        self.type = type
        self.url = url
        self.content = content
        self.user = user
        self.date = date

class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timezone = db.Column(db.String(10))
    night_time_on = db.Column(db.Integer)
    night_time_off = db.Column(db.Integer)
    night_mode_type = db.Column(db.String(10))
    font_size = db.Column(db.String(3))
    coding_addon = db.Column(db.Integer)
    hyperlinks_addon = db.Column(db.Integer)
    colors_addon = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, timezone, night_on, night_off, night_type, font_size, coding_addon, hyperlinks_addon, colors_addon, user_id):
        self.timezone = timezone
        self.night_time_on = night_on
        self.night_time_off = night_off
        self.night_mode_type = night_type
        self.font_size = font_size
        self.coding_addon = coding_addon
        self.hyperlinks_addon = hyperlinks_addon
        self.colors_addon = colors_addon
        self.user_id = user_id
