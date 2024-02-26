from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint
from blog import db
from blog.models import Announcement
from blog.announcements.forms import AnnouncementForm
from blog.decorators import admin_required

announcements = Blueprint('announcements', __name__)

@announcements.route("/announcements/new", methods=['GET', 'POST'])
def new_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data, start_date=form.start_date.data, end_date=form.end_date.data)
        db.session.add(announcement)
        db.session.commit()
        flash('Your announcement has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_announcement.html', title='New Announcement', form=form, legend='New Announcement')

@announcements.route("/announcements")
def list_announcements():
    page = request.args.get('page', 1, type=int)
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('announcements.html', announcements=announcements)