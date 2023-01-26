from InDev import db, login_manager
from InDev import bcrypt
from flask_login import UserMixin
from datetime import date


@login_manager.user_loader
def load_user(user_id):
    return Developer.query.get(int(user_id))


class Developer(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(length=30), nullable=False)
    last_name = db.Column(db.String(length=30))
    username = db.Column(db.String(), nullable=False, unique=True)
    email_address = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String(), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=0)
    date_added = db.Column(db.DateTime(), default=date.today())
    # Developer can have many posts
    posts = db.relationship('Post', backref='author')

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    date_added = db.Column(db.DateTime(), default=date.today())
    # Foreign key to refer to Developers
    author_id = db.Column(db.Integer, db.ForeignKey('developer.id'))


class Service(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
