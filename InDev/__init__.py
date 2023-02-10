from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_admin import Admin


# Create Flask Instance
app = Flask(__name__)
# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
# Migration
migrate = Migrate(app, db)
# Password encrypting
bcrypt = Bcrypt(app)
# Login
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'
# Secret key
app.config['SECRET_KEY'] = "b35199c4d1bab8f69da7227a"
# Rich Text Editor
ckeditor = CKEditor(app)
# Folder to save profile images
UPLOAD_FOLDER = 'InDev/static/pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from InDev import routes
