import hashlib
import re
from flask import (
    Blueprint, request, abort, jsonify
)
from vidcrypt import app, db, bcrypt
from vidcrypt.models import User



bp = Blueprint('identity', __name__, url_prefix='/identity')

@bp.route('/register', methods=(["POST"]))
def register():
    data = request.get_json()

    # Only allow alphanumeric usernames.
    username = data['username']
    if not username.isalnum():
        abort(400, {'errMessage': 'invalid username'})

    # Email must be at least syntactically valid.
    email = data['email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        abort(400, {'errMessage': 'invalid email'})

    # Password must be at least 8 characters long.
    password = data['password']
    if len(password) < 8:
        abort(400, {'errMessage': 'password too short'})
    # Hash password, because plaintext password storage is for squares.
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')


    # User must not already exist.
    if (User.query.filter_by(username = username).first() is not None and
        User.query.filter_by(email = email).first() is not None):
        abort(400, {'errMessage': 'duplicate username'})

    # Add new user to the DB
    user = User(username = username, email = email, password = password)
    db.session.add(user)
    db.session.commit()

    # TODO (Story4): Add email validation to confirm email address is real and belongs to user
    # send_registration_email(FROM_EMAIL, FROM_PASSWORD, email, EMAIL_SERVER, EMAIL_PORT)

    return jsonify({ 'username': user.username }), 201

@bp.route('/login', methods=(["POST"]))
def login():
    data = request.get_json()
    username = data['username']
    user = User.query.filter_by(username = username).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        abort(401, {'errMessage':'invalid username or password'})

    auth_token = hashlib.sha256(user.username + app.config['SECRET_KEY'])
    return jsonify({'token': auth_token.hexdigest()}), 200
