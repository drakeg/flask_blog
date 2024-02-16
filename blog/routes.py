from flask import render_template, url_for, flash, redirect
from blog.forms import RegistrationForm, LoginForm
from blog.models import User, Post
from blog import app

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    },
    {
        'author': 'John Doe',
        'title': 'Blog Post 3',
        'content': 'Third post content',
        'date_posted': 'April 22, 2018'
    }
]

@app.route('/')
def home():
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    title = 'About'
    return render_template('about.html', title=title)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'greg@drakeweb.org' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)