from flask import jsonify, request, g, abort, render_template
from vidcrypt import app, db, bcrypt
from vidcrypt.models import User, Video
from flask_httpauth import HTTPBasicAuth
from vidcrypt import msg

auth = HTTPBasicAuth()
EMAIL_SERVER = 'smtp.gmail.com'
EMAIL_PORT = 587
FROM_EMAIL = 'vidcrypt@gmail.com'
FROM_PASSWORD = 'cryptvid92'

def send_registration_email(from_address, password, to_address, host, port):
	msg_object = {
		"subject":"Welcome to VidCrypt!",
		"msg_text":"Welcome from the VidCrypt team!"
	}

	msg.send_email(from_address, password, to_address, host, port, msg_object)

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    username = data['username']
    email = data['email']

    # No data passed to POST request
    if username is None or hashed_password is None or email is None:
        abort(400)

    # User already exists
    if User.query.filter_by(email = email).first() is not None:
        abort(400)

    user = User(username = username, email = email, password = hashed_password)
    db.session.add(user)
    db.session.commit()

    send_registration_email(FROM_EMAIL, FROM_PASSWORD, email, EMAIL_SERVER, EMAIL_PORT)

    return jsonify({ 'username': user.username }), 201


@app.route("/record_video", methods=['GET'])
@auth.login_required
def record_video():
	
    # Get the user from the request
    username = request.authorization['username']
    current_user = User.query.filter_by(username = username).first()
     
    # Extract the video's SHA hash from the query parameters
    sha_string = request.args['sha']
    current_video = Video(sha_string = sha_string)

    # Assign the video sha to the user in the database
    current_user.videos.append(current_video)
    db.session.commit()

    return jsonify({ 'data': 'Inserted video associated with user'})

@app.route("/authenticate_video", methods=['GET'])
def authenticate_video():
	
    # Get video data from get request and retrieve videos, usernames
    sha_string = request.args['sha']
    video = db.session.query(Video, User.username).join(User)

    found = 0
    user = 'N/A'

    # Check if video matching query string is found and retrieve user associated with it
    for video, username in video:
	if video.sha_string == sha_string:
		found = 1
		user = username


    return jsonify({'data':{'found':found, 'user':user}})	

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return False

    g.user = user

    return True

@app.route("/")
def home():
    users = User.query.all()
    return render_template('home.html',users=users)
