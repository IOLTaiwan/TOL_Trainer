from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from flasktol import db, bcrypt
from flasktol.models import User, Question, Answer
from flasktol.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from flasktol.users.utils import save_picture, send_reset_email
from flask import Blueprint
users = Blueprint('users', __name__)

# register page


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in 您已登入', 'success')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you are now able to log in 您的帳號已經建立，您現在可以登入', 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title="Register 註冊", form=form)

# login page


@users.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash('You are already logged in 您已登入', 'success')
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in 您已登入', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful, please try again 登入失敗，請再試一次', 'danger')

    return render_template("login.html", title="Login 登入", form=form)

# logout route


@users.route("/logout")
def logout():
    flash('You have been logged out 您已登出', 'info')
    logout_user()
    return redirect(url_for('main.home'))

# account information (non-admin can only view their own)


@users.route("/account/<string:username>", methods=['GET', 'POST'])
@login_required
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.username != current_user.username and not current_user.is_admin():
        abort(403)
    # statistics
    answerlist = Answer.query.filter_by(user_id=user.id).all()
    q_set = set()
    attempted_count = 0
    highest_grade = {}
    for answer in answerlist:
        if answer.question_id not in q_set:
            q_set.add(answer.question_id)
            attempted_count += 1
        try:
            if answer.grade > highest_grade[answer.id]:
                highest_grade[answer.id] = answer.grade
        except:
            highest_grade[answer.id] = answer.grade
    total_score = sum(highest_grade.values())
    answers_submitted = len(answerlist)
    # form
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        user.username = form.username.data
        user.email = form.email.data
        user.access = int(form.access.data)
        db.session.commit()
        flash('Account has been updated 帳號已更新', 'success')
        return redirect(url_for('users.account', username=user.username))
    elif request.method == 'GET':
        form.access.process_data(str(user.access))
        form.username.data = user.username
        form.email.data = user.email
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template("account.html", title="Account 帳號", image_file=image_file, form=form, user=user, attempted_count=attempted_count, total_score=total_score, answers_submitted=answers_submitted)

# request password reset


@users.route("/request_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An password reset email has been sent 已發送電子郵件", "info")
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title="Reset Password 重置密碼", form=form)

# reset password


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token 鏈接無效或過期", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated 密碼已更新', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", title="Reset Password 重置密碼", form=form)

# list of users (admin only)


@users.route("/user_list")
@login_required
def user_list():
    if not current_user.is_admin():
        abort(403)
    userlist = User.query.all()
    return render_template("user_list.html", title="User List 用戶列表", userlist=userlist)
