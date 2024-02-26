from blog import create_app
from blog.extensions import db
from blog.models import Role
from blog.config import Config

SQLALCHEMY_DATABASE_URI='sqlite:///blog.db'

app = create_app()
app.app_context().push()

roles = ['User', 'Author', 'Admin']

for role_name in roles:
    if not Role.query.filter_by(name=role_name).first():
        role = Role(name=role_name)
        db.session.add(role)

db.session.commit()
