# admin.py
from blog.models import User, Post, Announcement
from flask import Blueprint, render_template, request

admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage_users')
def manage_users():
    users = User.query.all()  # Assuming a User model
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/add_user')
def add_user():
    return render_template('admin/add_user.html')

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user_id = request.args.get('user_id')

@admin_bp.route('/change_user_password/<int:user_id>', methods=['GET', 'POST'])
def change_user_password(user_id):
    user_id = request.args.get('user_id')

@admin_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user_id = request.args.get('user_id')

@admin_bp.route('/manage_posts')
def manage_posts():
    posts = Post.query.all()
    return render_template('admin/manage_posts.html', posts=posts)

@admin_bp.route('/manage_announcements')
def manage_announcements():
    announcements = Announcement.query.all()
    return render_template('admin/manage_announcements.html', announcements=announcements)