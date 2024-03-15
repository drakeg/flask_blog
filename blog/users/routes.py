import os
import secrets
import resend
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordRequestForm, ResetPasswordForm
from blog.models import User, Post, Role
from blog import db, bcrypt, logger
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from flask_mailman import EmailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from blog.decorators import email_confirmed_required
from blog.email import send_email

users_bp = Blueprint('users', __name__)
resend.api_key = os.environ.get('RESEND_KEY')

@users_bp.route('/register', methods=['GET', 'POST'])
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
            logger.error('The user roles have not been created.')
            db.session.add(user_role)
            db.session.commit()

        user = User(username=form.username.data,email=form.email.data, password=hashed_pw, role=user_role)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        send_email(user.email, "Account Confirmation", f"To confirm your account, visit the following link: {url_for('users.confirm_email', token=token, _external=True)}")
        flash(f'Your account has been created and a confirmation email sent!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users_bp.route("/confirm/<token>")
def confirm_email(token):
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    email = s.loads(token, salt='token-confirm', max_age=3600)
    if not email:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("users.login"))  # Redirect to login if the token is invalid

    user = User.query.filter_by(email=email).first_or_404()
    if not user.is_confirmed:
        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()  # Use UTC for consistency
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("Account already confirmed.", "info")
    return redirect(url_for("main.home"))

@users_bp.route('/login', methods=['GET', 'POST'])
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
            logger.info(f"Login successful for user with email address {form.email.data}")
            flash(f'Login successful!', 'success')
        else:
            logger.warning(f"Login failed for user with email address {form.email.data}")
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users_bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_confirmed:
        return redirect(url_for('main.home'))
    return render_template('unconfirmed.html')

@users_bp.route('/resend')
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    msg = EmailMessage(
        subject="Account Confirmation",
        body=f"To confirm your account, visit the following link: {url_for('users.confirm_email', token=token, _external=True)}",
        to=[current_user.email]
    )
    msg.send()
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('users.unconfirmed'))

@users_bp.route('/account', methods=['GET', 'POST'])
@login_required
@email_confirmed_required
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

@users_bp.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users_bp.route("/reset_password", methods=['GET', 'POST'])
@email_confirmed_required
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

@users_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    try:
        s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
        email = s.loads(token, salt='token-confirm', max_age=3600)
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

@users_bp.route('/api_key', methods=['GET', 'POST'])
@login_required
def api_key():
    if request.method == 'POST':
        current_user.generate_api_key()
        flash('Your API key has been generated!', 'success')
        return redirect(url_for('users.api_key'))
    return render_template('api_key.html', title='API Key', api_key=current_user.api_key)