from flask import Blueprint
from flask_restx import Api
from .posts.api import api as posts_ns
from .users.api import api as users_ns
from .announcements.api import api as announcements_ns
from .about.api import api as about_ns

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp, title="Fitness Blog", version="1.0", description="A blog about fitness")

api.add_namespace(posts_ns, path='/posts')
api.add_namespace(users_ns, path='/users')
api.add_namespace(announcements_ns, path='/announcements')
api.add_namespace(about_ns, path='/about')