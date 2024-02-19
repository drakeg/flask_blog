import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mailman import Mail

app = Flask(__name__)
mail = Mail()

app.config['SECRET_KEY'] = '63f9fcaa7a7bac656d1326258a8b16a5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'june5wed@gmail.com'
app.config['MAIL_PASSWORD'] = 'qmce iawm cbup niod'
app.config['MAIL_FILE_PATH'] = 'mail'
#app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
#app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail.init_app(app)

from blog import routes