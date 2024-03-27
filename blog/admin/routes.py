# admin.py
from blog import bcrypt, db
from blog.admin.forms import EditUserForm, ChangePasswordForm, AddUserForm, PostForm, AnnouncementForm, AboutForm, SiteSettingsForm
from blog.models import User, Post, Role, Announcement, Tag, AboutPageContent, SiteSettings
from blog.decorators import admin_required
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='templates/admin', static_folder='static')

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage_users')
@login_required
@admin_required
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

@admin_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(user_id):
    if not current_user.role.name == 'Admin':
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

@admin_bp.route('/add_post', methods=['GET', 'POST'])
@login_required
@admin_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        user = User.query.get(form.author.data)
        post = Post(title=form.title.data, content=form.content.data, user_id=user.id)
        tag_names = request.form['tags'].split(',')
        
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if not tag:
                # Create a new tag if it doesn't exist
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            post.tags.append(tag)

        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('admin_bp.manage_posts'))
    return render_template('admin/add_post.html', title='New Post', form=form, legend='New Post')

@admin_bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.author.data = post.user_id
        # Convert the post's tags to a comma-separated string
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.user_id = form.author.data
        # Handle tags updating
        submitted_tags = form.tags.data.split(',')
        submitted_tags = [tag.strip() for tag in submitted_tags if tag.strip()]
        
        post.tags = []
        for tag_name in submitted_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                # Create the tag if it does not exist
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('admin_bp.manage_posts'))
    return render_template('admin/edit_post.html', title='Update Post',
                           form=form, legend='Update Post', post=post)

@admin_bp.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_post(post_id):
    if not current_user.role.name == 'Admin':
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('main.home'))

    post = Post.query.get_or_404(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Post has been successfully deleted.', 'success')
    else:
        flash('Post not found.', 'warning')
    return redirect(url_for('admin_bp.manage_posts'))

@admin_bp.route('/manage_announcements')
@login_required
@admin_required
def manage_announcements():
    announcements = Announcement.query.all()
    return render_template('admin/manage_announcements.html', announcements=announcements)

@admin_bp.route('/add_announcement', methods=['GET', 'POST'])
@login_required
@admin_required
def add_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data, start_date=form.start_date.data, end_date=form.end_date.data)
        db.session.add(announcement)
        db.session.commit()
        flash('Your announcement has been created!', 'success')
        return redirect(url_for('admin_bp.manage_announcements'))
    return render_template('admin/add_announcement.html', title='New Announcement', form=form, legend='New Announcement')

@admin_bp.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    form = AnnouncementForm()
    if request.method == 'GET':
        form.title.data = announcement.title
        form.content.data = announcement.content
        form.start_date.data = announcement.start_date
        form.end_date.data = announcement.end_date
    
    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.content = form.content.data
        announcement.start_date = form.start_date.data
        announcement.end_date = form.end_date.data
        db.session.commit()
        flash('Your announcement has been updated!', 'success')
        return redirect(url_for('admin_bp.manage_announcements'))
    return render_template('admin/edit_announcement.html', title='Update Announcement',
                           form=form, legend='Update Announcement', announcement=announcement)
    
@admin_bp.route('/delete_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    if not current_user.role.name == 'Admin':
        flash('You must be an admin to perform this action.', 'danger')
        return redirect(url_for('main.home'))

    announcement = Announcement.query.get_or_404(announcement_id)
    if announcement:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement has been successfully deleted.', 'success')
    else:
        flash('Announcement not found.', 'warning')
    return redirect(url_for('admin_bp.manage_announcements'))

@admin_bp.route('/edit_about', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_about():
    about_content = AboutPageContent.query.first()
    if not about_content:
        # Initialize AboutPageContent if it does not exist
        about_content = AboutPageContent(content='')
        db.session.add(about_content)
        db.session.commit()

    form = AboutForm()
    if form.validate_on_submit():
        about_content.content = form.content.data
        db.session.commit()
        flash('The About page has been updated.', 'success')
        return redirect(url_for('admin_bp.admin_dashboard'))

    elif request.method == 'GET':
        form.content.data = about_content.content

    return render_template('admin/edit_about.html', title='Edit About Page', form=form)

@admin_bp.route('/edit_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_settings():
    site_settings = SiteSettings.query.first()
    if not site_settings:
        # Initialize SiteSettings if it does not exist
        site_settings = SiteSettings(site_name='My Site', site_email='admin@site.org', site_description='My site is awesome!')
        db.session.add(site_settings)
        db.session.commit()

    form = SiteSettingsForm()
    if form.validate_on_submit():
        site_settings.site_name = form.site_name.data
        site_settings.site_email = form.site_email.data
        site_settings.site_description = form.site_description.data
        db.session.commit()
        flash('The site settings have been updated.', 'success')
        return redirect(url_for('admin_bp.admin_dashboard'))
    elif request.method == 'GET':
        form.site_name.data = site_settings.site_name
        form.site_email.data = site_settings.site_email
        form.site_description.data = site_settings.site_description
        
    return render_template('admin/edit_settings.html', title='Edit Site Settings', form=form)