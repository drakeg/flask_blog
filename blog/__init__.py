from datetime import datetime
import os
from blog.extensions import db, login_manager
from flask import Flask
from flask_pagedown import PageDown
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_mailman import Mail
from flask_migrate import Migrate
from blog.config import Config
from blog.models import Post, Announcement
from blog.commands import register_commands
from logtail import LogtailHandler
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

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db, compare_type=True, render_as_batch=True)
    pagedown = PageDown(app)

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

    return app