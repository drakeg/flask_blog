from flask_login import current_user
from functools import wraps
from flask import flash, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Assuming 'Admin' is the role name for administrators
        if not current_user.is_authenticated or current_user.role.name != 'Admin':
            flash('This area is restricted to administrators only.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def author_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Assuming 'Author' is the role name for authors
        if not current_user.is_authenticated or current_user.role.name != 'Author':
            flash('This area is restricted to authors only.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_author_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('user.login'))
        elif not (current_user.role.name == 'Admin' or current_user.role.name == 'Author'):
            flash('This page requires admin or author access.', 'warning')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function