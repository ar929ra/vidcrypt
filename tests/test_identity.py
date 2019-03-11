import hashlib
import os
import pytest
import tempfile
from vidcrypt import app, bcrypt, db
from vidcrypt.models import User

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    #db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(tempfile.gettempdir(), 'test.db')
	
    db.drop_all() # Drop existing tables so tests don't run into duplicate user issues when run multiple times.
    db.create_all()

    return app.test_client()

valid_username = 'janedoe123'
valid_email = 'janedoe@janedoe.com'
valid_password = 'eight888'
valid_hashed_password = bcrypt.generate_password_hash(valid_password).decode('utf-8')

def test_register(client):
    """Tests for the `register` function of the identity blueprint"""
    # A valid request should add a user to the database, then return a valid response containing the supplied username
    response = client.post(
        '/identity/register', json={'username':valid_username, 'email': valid_email, 'password':valid_password}
    )
    assert User.query.filter_by(username = valid_username).first() is not None
    assert 201 == response.status_code
    assert valid_username == response.get_json()['username']

    # an invalid (i.e. non-alphanumeric) username should return an error
    test_cases = ["jane doe", "jane doe?", "{'username':'janedoe'}"]
    for case in test_cases:
        response = client.post(
            'identity/register', json={'username':case, 'email': valid_email, 'password':valid_password}
        )
        assert 400 == response.status_code

    # an invalid email should return an error
    test_cases = ["janedoe.com", "jane@doe", "janedoeatjanedoedotcom"]
    for case in test_cases:
        response = client.post(
            'identity/register', json={'username':valid_username, 'email': case, 'password':valid_password}
        )
        assert 400 == response.status_code
    
    # an invalid (i.e. too short) password should return an error
    response = client.post(
        'identity/register', json={'username':valid_username, 'email': valid_email, 'password':'seven77'}
    )
    assert 400 == response.status_code

    
def test_login(client): 
    """Tests for the `login` function of the identity blueprint"""
    user = User(username = valid_username, email = valid_email, password = valid_hashed_password)
    db.session.add(user)
    db.session.commit()

    # a valid username/password combo should return a response with an auth token
    response = client.post(
        '/identity/login', json={'username':valid_username, 'password':valid_password}
    )
    assert 200 == response.status_code
    expected_token = hashlib.sha256(valid_username + app.config['SECRET_KEY']).hexdigest()
    assert expected_token == response.get_json()["token"]
    
    # an invalid username should return an error
    response = client.post(
        '/identity/login', json={'username':'invaliduser', 'password':valid_password}
    )
    assert 401 == response.status_code

    # an invalid password should return an error
    response = client.post(
        '/identity/login', json={'username':valid_username, 'password':'justguessing1234'}
    )
    assert 401 == response.status_code
