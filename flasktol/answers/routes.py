from flask import Blueprint
from flasktol.models import User, Question, Answer
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flasktol import db
from flasktol.answers.forms import AnswerForm, GradeForm
from flasktol.answers.utils import save_picture, save_pdf
import os
from flasktol import db, bcrypt
from flask import Blueprint
answers = Blueprint('answers', __name__)

# submit new answer (view depends on access)
@answers.route("/answers/new/<int:question_id>", methods=['GET', 'POST'])
@login_required
def new_answer(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if question.access > 1 and not current_user.is_authenticated:
        abort(403)
    elif current_user.is_authenticated:
        if question.access > current_user.access:
            abort(403)
    if form.validate_on_submit():
        if form.content_file.data:
            _, f_ext = os.path.splitext(form.content_file.data.filename)
            if f_ext == '.pdf':
                content = save_pdf(form.content_file.data)
            else:
                content = save_picture(form.content_file.data)
            answer = Answer(user_id=current_user.id, question_id=question.id, content=form.content.data, content_file=content)
        else:
            answer = Answer(user_id=current_user.id, question_id=question.id, content=form.content.data)
        db.session.add(answer)
        db.session.commit()
        flash("Your answer has been submitted 已送出答案", 'success')
        return redirect(url_for("questions.question", question_id=question.id))
    return render_template("submit_answer.html", title="Submit Answer 答題", form=form, legend="Submit Answer 答題", question=question)


# list of all answers (admin only)
@answers.route("/answer_list")
@login_required
def answer_list():
    if not current_user.is_admin():
        abort(403)
    answerlist = Answer.query.order_by(Answer.date_submitted.desc())
    return render_template('answer_list.html', title="Answer List 答題列表", answerlist=answerlist, legend="Answer List 答題列表")

# my answers (current user only)
@answers.route("/my_answers")
@login_required
def my_answers():
    answerlist = Answer.query.filter_by(user_id=current_user.id).order_by(Answer.date_submitted.desc())
    return render_template('my_answers.html', title="My Answers 我的答案", answerlist=answerlist, legend="My Answers")

# view answer (non-admin can only view their own)
@answers.route("/answer/<int:answer_id>")
@login_required
def answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if not current_user.is_admin() and current_user.id != answer.answerer.id:
        abort(403)
    if answer.content_file:
        content_file = url_for('static', filename='answer_files/' + answer.content_file)
        _, f_ext = os.path.splitext(answer.content_file)
        if f_ext == '.pdf':
            return render_template('answer.html', content_file=content_file, answer=answer, ispdf=True)
        else:
            return render_template('answer.html', content_file=content_file, answer=answer, ispdf=False)
    else:
        return render_template('answer.html', title="Answer 答題",answer=answer, ispdf=False)

# grade answer (admin only)
@answers.route("/answer/grade/<int:answer_id>", methods=['GET', 'POST'])
@login_required
def grade_answer(answer_id):
    if not current_user.is_admin():
        abort(403)
    answer = Answer.query.get_or_404(answer_id)
    form = GradeForm()
    if form.validate_on_submit():
        answer.grade=form.grade.data
        db.session.commit()
        flash("Score has been updated 已更新評分", 'success')
        return redirect(url_for('answers.answer_list'))
    elif request.method == 'GET':
        form.grade.data = answer.grade
    return render_template('grade_answer.html', title="Grade answer 答題評分", form=form, legend="Grade answer 答題評分")

@answers.route("/users_grades")
@login_required
def users_grades():
    if not current_user.is_admin():
        abort(403)
    answerlist = Answer.query.order_by(Answer.date_submitted.desc())
    questionlist = Question.query.all()
    userlist= User.query.all()

    latest_grade = {}
    highest_grade={}
    for answer in answerlist:
        if answer.user_id in latest_grade:
            if answer.question_id in latest_grade[answer.user_id]:
                if answer.grade>highest_grade[answer.user_id][answer.question_id][0]:
                    highest_grade[answer.user_id][answer.question_id]=(answer.grade,answer.id)
            else:
                latest_grade[answer.user_id][answer.question_id]=(answer.grade,answer.id)
                highest_grade[answer.user_id][answer.question_id]=(answer.grade,answer.id)
        else:
            latest_grade[answer.user_id]={answer.question_id:(answer.grade,answer.id)}
            highest_grade[answer.user_id]={answer.question_id:(answer.grade,answer.id)}

    score_sum={}
    for userid, useranswers in highest_grade.items():
        for questionid, useranswer in useranswers.items():
            try:
                score_sum[userid]+=useranswer[0]
            except:
                score_sum[userid]=useranswer[0]

    return render_template('users_grades.html',answerlist=answerlist,questionlist=questionlist,userlist=userlist, latest_grade=latest_grade,highest_grade=highest_grade, score_sum=score_sum, title="Users grades 用戶分數", legend="sers grades 用戶分數")