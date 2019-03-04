from flask import jsonify, request, g, abort
from vidcrypt import app, db, bcrypt
from vidcrypt.models import User
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@app.route("/register", methods=['POST'])
def register():
    data = request.json
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    username = data['username']
    email = data['email']

    # No data passed to POST request
    if username is None or hashed_password is None or email is None:
        abort(400)

    # User already exists
    if User.query.filter_by(email = email).first() is not None:
        abort(400)

    user = User(username = data['username'], email = data['email'], password = hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({ 'username': user.username }), 201


@app.route("/do_this", methods=['GET'])
@auth.login_required
def do_this():
    return jsonify({ 'data': 'Hi {0}!'.format(g.user) })

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email = email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return False

    g.user = user

    return True

@app.route("/")
def home():
    return "This is the vid crypt API"