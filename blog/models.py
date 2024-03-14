import bleach
import os
from blog import login_manager
from blog.extensions import db
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from hashlib import md5
from markdown import markdown

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for the many-to-many relationship
posts_tags = db.Table('posts_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def generate_token(self):
        serializer = Serializer(os.environ.get('SECRET_KEY'), salt="token-confirm")
        return serializer.dumps(self.email)

    def confirm_token(token, expiration=3600):
        serializer = Serializer(os.environ.get('SECRET_KEY'), salt="token-confirm")
        try:
            email = serializer.loads(token, salt="token-confirm", max_age=expiration)
        except Exception:
            return False
        user = User.query.filter_by(email=email).first()
        if not user:
            return False
        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.commit()
        return True

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary=posts_tags, lazy='subquery',
                           backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        'h1', 'h2', 'h3', 'p']
        target.content_html = bleach.linkify(bleach.clean(
        markdown(value, output_format='html'),
        tags=allowed_tags, strip=True))
db.event.listen(Post.content, 'set', Post.on_changed_content)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.String())
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date_posted}')"

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        'h1', 'h2', 'h3', 'p']
        target.content_html = bleach.linkify(bleach.clean(
        markdown(value, output_format='html'),
        tags=allowed_tags, strip=True))
db.event.listen(Announcement.content, 'set', Announcement.on_changed_content)

class AboutPageContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.String())

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        'h1', 'h2', 'h3', 'p']
        target.content_html = bleach.linkify(bleach.clean(
        markdown(value, output_format='html'),
        tags=allowed_tags, strip=True))
db.event.listen(AboutPageContent.content, 'set', AboutPageContent.on_changed_content)