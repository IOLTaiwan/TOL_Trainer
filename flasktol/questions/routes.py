from flask import Blueprint, request
from flasktol.models import User, Question, Answer
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flasktol import db
from flasktol.questions.forms import QuestionForm, UpdateQuestionForm
from flasktol.questions.utils import q_save_picture, q_save_pdf,s_save_picture, s_save_pdf
import os
from flasktol import db, bcrypt
questions = Blueprint('questions', __name__)

# add new question (admin only)
@questions.route("/questions/new", methods=['GET', 'POST'])
@login_required
def new_question():
    if not current_user.is_admin():
        abort(403)
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question()
        if form.content_file.data:
            _, f_ext = os.path.splitext(form.content_file.data.filename)
            if f_ext == '.pdf':
                content = q_save_pdf(form.content_file.data)
            else:
                content = q_save_picture(form.content_file.data)
            question.content_file=content
        if form.solution_file.data:
            _, f_ext = os.path.splitext(form.solution_file.data.filename)
            if f_ext == '.pdf':
                content = s_save_pdf(form.solution_file.data)
            else:
                content = s_save_picture(form.solution_file.data)
            question.solution_file=content
        question.title = form.title.data
        question.content = form.content.data
        question.access=int(form.access.data)
        question.difficulty=int(form.difficulty.data)
        question.tags=", ".join(form.tags.data)
        question.source=form.source.data
        question.solution=form.solution.data
        question.special_characters=form.special_characters.data
        question.open_solution=form.open_solution.data
        db.session.add(question)
        db.session.commit()
        flash("Your question has been created 已新增題目", 'success')
        return redirect(url_for('main.home'))
    return render_template("create_question.html", title="New Question 新增題目", form=form, legend="New Question 新增題目")

# list of all questions (view depends on access)
@questions.route("/question_list/<string:sort_type>/<string:a_d_order>")
def question_list(sort_type,a_d_order):
    if a_d_order=="a":
        if sort_type=="id":
            questionlist = Question.query.order_by(Question.id.asc())
        if sort_type=="date":
            questionlist = Question.query.order_by(Question.date_posted.asc())
        if sort_type=="title":
            questionlist = Question.query.order_by(Question.title.asc())
        elif sort_type=="source":
            questionlist = Question.query.order_by(Question.source.asc())
        elif sort_type=="difficulty":
            questionlist = Question.query.order_by(Question.difficulty.asc())
        elif sort_type=="type":
            questionlist = Question.query.order_by(Question.tags.asc())
        elif sort_type=="availability":
            questionlist = Question.query.order_by(Question.access.asc())
    elif a_d_order=="b":
        if sort_type=="id":
            questionlist = Question.query.order_by(Question.id.desc())
        if sort_type=="date":
            questionlist = Question.query.order_by(Question.date_posted.desc())
        if sort_type=="title":
            questionlist = Question.query.order_by(Question.title.desc())
        elif sort_type=="source":
            questionlist = Question.query.order_by(Question.source.desc())
        elif sort_type=="difficulty":
            questionlist = Question.query.order_by(Question.difficulty.desc())
        elif sort_type=="type":
            questionlist = Question.query.order_by(Question.tags.desc())
        elif sort_type=="availability":
            questionlist = Question.query.order_by(Question.access.desc())
    return render_template('question_list.html', title="Question List 題目列表", questionlist=questionlist, legend="Question List 題目列表",sort_type=sort_type,a_d_order=a_d_order)

# question details (view depends on access)
@questions.route("/question/<int:question_id>")
def question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.access > 1 and not current_user.is_authenticated:
        abort(403)
    elif current_user.is_authenticated:
        if question.access > current_user.access:
            abort(403)
    if current_user.is_authenticated:
        if current_user.is_admin():
            answerlist = Answer.query.filter_by(question_id=question.id).order_by(Answer.date_submitted.desc())
        else:
            answerlist = Answer.query.filter_by(question_id=question.id, user_id=current_user.id).order_by(Answer.date_submitted.desc())
    else:
        answerlist = []
    if question.content_file:
        content_file = url_for('static', filename='question_files/' + question.content_file)
        _, f_ext = os.path.splitext(question.content_file)
        if f_ext == '.pdf':
            ispdf=True
        else:
            ispdf=False
    else:
        content_file=None
        ispdf=False
    return render_template('question.html', title=question.title, content_file=content_file, question=question, ispdf=ispdf, answerlist=answerlist)

# update question (admin only)
@questions.route("/question/<int:question_id>/update", methods=['GET', 'POST'])
@login_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    if not current_user.is_admin():
        abort(403)
    form = UpdateQuestionForm()
    if form.validate_on_submit():
        question.title = form.title.data
        question.content = form.content.data
        if form.content_file.data:
            _, f_ext = os.path.splitext(form.content_file.data.filename)
            if f_ext == '.pdf':
                content = q_save_pdf(form.content_file.data)
            else:
                content = q_save_picture(form.content_file.data)
            question.content_file = content
        if form.solution_file.data:
            _, f_ext = os.path.splitext(form.solution_file.data.filename)
            if f_ext == '.pdf':
                content = s_save_pdf(form.solution_file.data)
            else:
                content = s_save_picture(form.solution_file.data)
            question.solution_file = content
        question.access=int(form.access.data)
        question.difficulty=int(form.difficulty.data)
        question.tags=form.tags.data
        question.source=form.source.data
        question.solution=form.solution.data
        question.special_characters=form.special_characters.data
        question.open_solution=form.open_solution.data
        db.session.commit()
        flash("Question has been updated 已更新題目", 'success')
        return redirect(url_for('questions.question', question_id=question.id))
    elif request.method == 'GET':
        form.title.data = question.title
        form.content.data = question.content
        form.tags.data=question.tags
        form.access.process_data(str(question.access))
        form.difficulty.process_data(str(question.difficulty))
        form.open_solution.process_data(str(question.open_solution))
        form.source.data=question.source
        form.solution.data=question.solution
        form.special_characters.data=question.special_characters
    return render_template('update_question.html', title="Update question 更新題目", form=form, legend="Update question 更新題目")

# delete question (admin only)
@questions.route("/question/<int:question_id>/delete", methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    if not current_user.is_admin():
        abort(403)
    answer = Answer.query.filter_by(question_id=question.id).all()
    for ans in answer:
        db.session.delete(ans)
    db.session.delete(question)
    db.session.commit()
    flash("Question has been deleted 已刪除題目", 'success')
    return redirect(url_for('questions.question_list',sort_type="id",a_d_order="b"))

# view solutions (admin only / available to all if question.open_solution is True)
@questions.route("/question/<int:question_id>/solution")
def solution(question_id):
    question = Question.query.get_or_404(question_id)
    if current_user.is_authenticated:
        if not current_user.is_admin() and not question.open_solution:
            abort(403)
    else:
        if not question.open_solution:
            abort(403)
    if question.solution_file:
        solution_file = url_for('static', filename='solution_files/' + question.solution_file)
        _, f_ext = os.path.splitext(question.solution_file)
        if f_ext == '.pdf':
            ispdf=True
        else:
            ispdf=False
    else:
        solution_file=None
        ispdf=False
    return render_template('solution.html', title="View solution 解答", legend="View solution 解答", question=question, solution_file=solution_file, ispdf=ispdf)