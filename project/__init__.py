import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import pymysql
import project.core.secrets as secrets


db_conn = "mysql+pymysql://{}:{}@{}/{}".format(secrets.db_user, secrets.db_pass, secrets.db_host, secrets.db_name)

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = secrets.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
Migrate(app,db)

app.config['MAIL_SERVER'] = 'mail.sensworks.ca'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = secrets.email_username
app.config['MAIL_PASSWORD'] = secrets.email_password
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'


from project.error_pages.handlers import error_pages
app.register_blueprint(error_pages)

from project.core.views import core
app.register_blueprint(core)

from project.admin.views import admin
app.register_blueprint(admin, url_prefix = "/admin")


from project.users.views import accounts
app.register_blueprint(accounts, url_prefix = "/users")

from project.desks.views import desks
app.register_blueprint(desks, url_prefix = "/desks")

from project.notebooks.views import notebooks
app.register_blueprint(notebooks, url_prefix = "/u")

from project.pages.views import pages
app.register_blueprint(pages, url_prefix="/nb")
