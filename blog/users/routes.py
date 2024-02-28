import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, Blueprint
from blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordRequestForm, ResetPasswordForm
from blog.models import User, Post, Role
from blog import db, bcrypt
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from flask_mailman import EmailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(f"You are already registered.", "info")
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Query the database for the "User" role
        user_role = Role.query.filter_by(name='User').first()
        # Fallback in case the role doesn't exist, though you should ensure it does via migrations/seeding
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
            db.session.commit()

        user = User(username=form.username.data,email=form.email.data, password=hashed_pw, role=user_role)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        msg = EmailMessage(
            subject="Account Confirmation",
            body=f"To confirm your account, visit the following link: {url_for('users.confirm_email', token=token, _external=True)}",
            to=[user.email]
        )
        msg.send()
        flash(f'Your account has been created and a confirmation email sent!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("core.home"))
    email = user.confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("core.home"))

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
            print(f"User role: {user.role}")
            flash(f'Login successful!', 'success')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account',
                           form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_token()
            msg = EmailMessage(
                subject="Password Reset Request",
                body=f"To reset your password, visit the following link: {url_for('users.reset_token', token=token, _external=True)}",
                to=[user.email]
            )
            msg.send()
            flash('An email has been sent with instructions to reset your password, if an account with that email exists..', 'info')
        else:
            flash('An email has been sent with instructions to reset your password, if an account with that email exists..', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    try:
        s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
        email = s.loads(token, salt='email-reset', max_age=3600)
    except SignatureExpired:
        flash('The password reset link is expired.', 'warning')
        return redirect(url_for('users.reset_password_request'))
    
    user = User.find_by_email(email)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return redirect(url_for('users.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()  # Assuming you have a db session and commit setup
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', token=token, form=form)