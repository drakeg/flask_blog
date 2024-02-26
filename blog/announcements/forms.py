from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import date

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    submit = SubmitField('Post Announcement')