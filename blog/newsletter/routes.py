from flask import Blueprint, render_template, flash, redirect, url_for
from yourapp.models import NewsletterSubscription
from yourapp.forms import NewsletterForm
from yourapp.extensions import db

main = Blueprint('main', __name__)

@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = NewsletterForm()
    if form.validate_on_submit():
        if NewsletterSubscription.query.filter_by(email=form.email.data).first():
            flash('You have already subscribed to the newsletter!', 'info')
        else:
            subscription = NewsletterSubscription(email=form.email.data)
            db.session.add(subscription)
            db.session.commit()
            flash('You have successfully subscribed to the newsletter!', 'success')
        return redirect(url_for('main.index'))
    return render_template('subscribe.html', form=form)