# admin.py
from blog import bcrypt, db
from blog.admin.forms import EditUserForm, ChangePasswordForm, AddUserForm
from blog.models import User, Post, Role, Announcement
from blog.decorators import admin_required
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='templates/admin', static_folder='static')

@admin_bp.route('/')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage_users')
def manage_users():
    users = User.query.all()  # Assuming a User model
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        role = Role.query.get(form.role.data)  # Retrieve the selected role
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, role=role, 
                    is_confirmed=form.is_confirmed.data)
        db.session.add(user)
        db.session.commit()
        flash('New user has been added.', 'success')
        return redirect(url_for('admin_bp.manage_users'))
    return render_template('admin/add_user.html', title='Add New User', form=form)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        user.is_confirmed = form.is_confirmed.data
        db.session.commit()
        flash('User has been updated.', 'success')
        return redirect(url_for('admin_bp.manage_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role_id
        form.is_confirmed.data = user.is_confirmed
    return render_template('admin/edit_user.html', title='Edit User', form=form, user_id=user_id)

@admin_bp.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('User password has been updated.', 'success')
        return redirect(url_for('admin_bp.manage_users'))
    
    return render_template('admin/change_user_password.html', title='Change User Password', form=form, user=user)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User has been successfully deleted.', 'success')
    else:
        flash('User not found.', 'warning')
    return redirect(url_for('admin_bp.manage_users'))

@admin_bp.route('/manage_posts')
@login_required
@admin_required
def manage_posts():
    posts = Post.query.all()
    return render_template('admin/manage_posts.html', posts=posts)

@admin_bp.route('/add_post')
@login_required
@admin_required
def add_post():
    return render_template('add_post.html')

@admin_bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    post_id = request.args.get('post_id')
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('admin/add_post.html', title='Update Post',
                           form=form, legend='Update Post')


@admin_bp.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_post(post_id):
    post_id = request.args.get('post_id')

@admin_bp.route('/manage_announcements')
@login_required
@admin_required
def manage_announcements():
    announcements = Announcement.query.all()
    return render_template('admin/manage_announcements.html', announcements=announcements)

@admin_bp.route('/add_announcement')
@login_required
@admin_required
def add_announcement():
    return render_template('admin/add_announcement.html')

@admin_bp.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(announcement_id):
    announcement_id = request.args.get('announcement_id')
    
@admin_bp.route('/delete_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    announcement_id = request.args.get('announcement_id')