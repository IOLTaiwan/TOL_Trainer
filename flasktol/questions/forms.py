from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, BooleanField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired

class MultiCheckboxField(SelectMultipleField):
	widget=ListWidget(prefix_label=False)
	option_widget=CheckboxInput()

class QuestionForm(FlaskForm):
    title = StringField('Title 標題', validators=[DataRequired()])
    content = TextAreaField('Description 備註')
    content_file = FileField('Content File 檔案 (.jpg, .png, .pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    access = SelectField("Access level 權限", validators=[DataRequired()], choices=[('1', "Guest 一般"), ('2', "Trainee 國手"), ('3', "Admin 管理員")])
    difficulty = SelectField("Difficulty 難易度", validators=[DataRequired()], choices=[('1', "1"), ('2', "2"), ('3', "3"),('4', "4"),('5', "5")])
    tags= MultiCheckboxField("Type 類型", choices=[('Phonology 音素學',"Phonology 音素學"), ('Morphology 構詞學', "Morphology 構詞學"), ('Syntax 語法學', "Syntax 語法學"),('Semantics 語義學',"Semantics 語義學"),('Maths 數學', "Maths 數學"),('Writing systems 文字系統',"Writing systems 文字系統"),('Culture 文化',"Culture 文化"), ('Sociolinguistics 社會語言學',"Sociolinguistics 社會語言學"),('Historical Linguistics 歷史語言學',"Historical Linguistics 歷史語言學"),('Computational linguistics 電腦語言學',"Computational Linguistics 電腦語言學")])
    source = StringField('Source 出處')
    open_solution=BooleanField("Open View Solution 開放檢視答案")
    solution = TextAreaField('Solution 解答')
    solution_file= FileField('Content File 檔案 (.jpg, .png, .pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    special_characters=TextAreaField('Special Characters 特殊字元')
    submit = SubmitField("Create 建立")


class UpdateQuestionForm(FlaskForm):
    title = StringField('Title 標題', validators=[DataRequired()])
    content = TextAreaField('Description 備註')
    content_file = FileField('Content File 檔案 (.jpg, .png, .pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    access = SelectField("Access level 權限", validators=[DataRequired()], choices=[('1', "Guest 一般"), ('2', "Trainee 國手"), ('3', "Admin 管理員")])
    difficulty = SelectField("Difficulty 難易度", validators=[DataRequired()], choices=[('1', "1"), ('2', "2"), ('3', "3"),('4', "4"),('5', "5")])
    tags= TextAreaField("Type 類型")
    source = StringField('Source 出處')
    open_solution=BooleanField("Open View Solution 開放檢視答案")
    solution = TextAreaField('Solution 解答')
    solution_file = FileField('Content File 檔案 (.jpg, .png, .pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    special_characters=TextAreaField('Special Characters 特殊字元')
    submit = SubmitField("Update 更新")