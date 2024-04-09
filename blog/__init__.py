from datetime import datetime
import os
from blog.extensions import db, login_manager
from flask import Flask
from flask_pagedown import PageDown
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_jwt_extended import JWTManager
from flask_mailman import Mail
from flask_migrate import Migrate
from blog.config import Config
from blog.models import Post, Announcement, SiteSettings
from blog.commands import register_commands
from blog.utilities import get_site_settings
from logtail import LogtailHandler
from sqlalchemy import MetaData
import logging

handler = LogtailHandler(source_token=os.environ.get('LOGTAIL_TOKEN'))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)

bcrypt = Bcrypt()
ckeditor = CKEditor()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    db.init_app(app)
    bcrypt.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db, compare_type=True, render_as_batch=True, metadata=metadata)
    pagedown = PageDown(app)
    jwt = JWTManager(app)

    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'

    from blog.models import Post
    from blog.announcements.routes import announcements_bp
    from blog.users.routes import users_bp
    from blog.posts.routes import posts_bp
    from blog.main.routes import main_bp
    from blog.errors.handlers import errors_bp
    from blog.admin.routes import admin_bp
    from blog.api import api_bp
    app.register_blueprint(announcements_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register CLI commands
    register_commands(app)

    @app.context_processor
    def inject_latest_posts():
        latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(3).all()
        return dict(latest_posts=latest_posts)

    @app.context_processor
    def inject_announcements():
        current_date = datetime.utcnow()
        active_announcements = Announcement.query.filter(Announcement.start_date <= current_date,
                                                Announcement.end_date >= current_date)\
                                        .order_by(Announcement.date_posted.desc()).all()
        print(active_announcements)
        return dict(active_announcements=active_announcements)

    @app.context_processor
    def inject_site_settings():
        settings = get_site_settings()
        if settings:
            return {
                'site_name': settings.site_name,
                'site_description': settings.site_description,
                'site_email': settings.site_email
            }
        return {}

    return app