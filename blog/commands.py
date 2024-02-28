import click
from flask.cli import with_appcontext
from flask_bcrypt import Bcrypt
import getpass
from blog.extensions import db
from blog.models import User, Role
from datetime import datetime

bcrypt = Bcrypt()

@click.command(name='create_roles')
@with_appcontext
def create_roles():
    """Create User, Author, and Admin roles."""
    roles = ['User', 'Author', 'Admin']

    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()
    print("Roles created successfully.")

@click.command(name='create_admin')
@with_appcontext
def create_admin():
    """Creates the admin user."""
    username = click.prompt("Enter a username", type=str)
    email = click.prompt("Enter email address", type=str)
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")

    if password != confirm_password:
        print("Passwords don't match.")
        return

    hashed_password = bcrypt.generate_password_hash(password)
    admin_role = Role.query.filter_by(name='Admin').first()

    if admin_role:
        user = User(username=username, email=email, password=hashed_password, role=admin_role, is_confirmed=True, confirmed_on=datetime.now())  # Adjust based on your User model
        db.session.add(user)
        db.session.commit()
        print(f"Admin with email {email} created successfully!")
    else:
        print("Admin role does not exist.")

def register_commands(app):
    """Register custom commands for the Flask CLI."""
    app.cli.add_command(create_roles)
    app.cli.add_command(create_admin)