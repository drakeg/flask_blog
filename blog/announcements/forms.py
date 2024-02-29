from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import date
from flask_pagedown.fields import PageDownField

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = PageDownField('Content', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    submit = SubmitField('Post Announcement')