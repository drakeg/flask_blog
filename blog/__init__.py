from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Post

app = Flask(__name__)

app.config['SECRET_KEY'] = '63f9fcaa7a7bac656d1326258a8b16a5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from blog import routes