from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


class AnswerForm(FlaskForm):
    content = TextAreaField('Answer 答案')
    content_file = FileField('Content File 檔案 (.jpg, .png, .pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    submit = SubmitField('Create 建立')


class GradeForm(FlaskForm):
    grade = IntegerField('Grade')
    submit = SubmitField('Save')
