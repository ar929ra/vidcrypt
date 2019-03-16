import os
import unittest

from flask import request, jsonify
from vidcrypt import app, db
from vidcrypt.models import User
from requests.auth import _basic_auth_str

basedir = os.path.abspath(os.path.dirname(__file__))

class TestCase(unittest.TestCase):

	def setUp(self):
		''' Sets up the test app and db '''
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		
		self.client = app.test_client()
		db.create_all()

	def tearDown(self):
		''' Deletes the DB session and drops all tables '''
		db.session.remove()
		db.drop_all()
	
	def test_db(self):
		''' Deletes all of the records in the test DB and ensures that the base DB code is working  '''
		db.session.query(User).delete()
		
		res = self.client.get('/')
		
		assert len(res.data) == 98 

	def test_register(self, do_assert = 1):
		''' Test the register route and ensure a user has been created '''
		rv = self.client.post('/register', json = {
			'username':'flask', 'email':'flask@gmail.com', 'password':'secret'
		})

		json_data = rv.get_json()
			
		if do_assert == 1:
			assert json_data['username'] == 'flask'

	def test_record_video(self, do_assert = 1):
		''' Test an arbitrary protected API service '''
		self.test_register(0)
		headers = {
			'Authorization': _basic_auth_str('flask', 'secret')
		}

		res = self.client.get('/record_video', query_string={'sha':'1234abcdef'}, headers = headers)
		
		if do_assert == 1:
			assert res.status_code == 200

	def test_authenticate_video(self):
		self.test_record_video(0)
		
		res = self.client.get('/authenticate_video', query_string={'sha':'1234abcdef'})
		print(res.get_data(as_text=True))
		assert res.status_code == 200

if __name__ == '__main__':
	unittest.main()
