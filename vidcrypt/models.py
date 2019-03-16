from vidcrypt import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

    videos = db.relationship('Video', backref = 'user', lazy = True)


class Video(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	sha_string = db.Column(db.String(500), nullable = False)
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
