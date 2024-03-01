from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import date
from flask_pagedown.fields import PageDownField
from flask_ckeditor import CKEditorField

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    submit = SubmitField('Post Announcement')