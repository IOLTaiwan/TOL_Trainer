from flasktol import db, login_manager
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    access = db.Column(db.Integer, nullable=False, default=1)
    answers = db.relationship('Answer', backref='answerer', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'User("{self.username}","{self.email}","{self.image_file}")'

    def is_admin(self):
        return self.access == 3

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text)
    content_file = db.Column(db.String(20))
    access = db.Column(db.Integer, nullable=False, default=1)
    difficulty = db.Column(db.Integer, nullable=False, default=1)
    tags= db.Column(db.Text)
    source = db.Column(db.String(100))
    solution = db.Column(db.Text)
    solution_file= db.Column(db.String(20))
    open_solution= db.Column(db.Boolean, nullable=False, default=False)
    special_characters=db.Column(db.Text)
    answers = db.relationship('Answer', backref='solveq', lazy=True)

    def __repr__(self):
        return f"Question('{self.title}','{self.date_posted}')"


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    content_file = db.Column(db.String(20))
    date_submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    grade = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Answer('{self.user_id}','{self.question_id}','{self.date_posted}')"
