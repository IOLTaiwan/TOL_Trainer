from flask import Blueprint
from flask import render_template, request, Blueprint
from flasktol.models import Question, User, Answer
from flasktol import db
main = Blueprint('main', __name__)
# home page


@main.route("/")
@main.route("/home")
def home():
	# user = User.query.filter_by(username="kchen").first_or_404()
	# user.access=3
	# db.session.commit()
	return render_template("home.html")

# questions page


@main.route("/questions")
def questions():
	page = request.args.get('page', 1, type=int)
	questions = Question.query.order_by(Question.date_posted.desc()).paginate(page=page, per_page=10)
	return render_template("questions.html", title="Questions", questions=questions)
