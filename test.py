import unittest
import os
import tempfile
import json
from employee_api import app, db
from employee_api.models import User, Employee



class TestAllEndPoints(unittest.TestCase):
	def setUp(self):
		self.test_db_file = tempfile.TemporaryDirectory().name
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+self.test_db_file
		app.config['TESTING'] = True
		self.app = app.test_client()
		with app.app_context():
			db.create_all()
		password = User.hash_password('12345678')
		user = User(email='test@test.com',password=password)
		user.create_user()
		
	def tearDown(self):
		os.remove(self.test_db_file)
		db.session.close_all()
		db.drop_all()
		
	
	def test_home(self)	:
		resp = self.app.get('/api/v1/', content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('It' in json.loads(resp.data))
		
	def test_signup(self):
		user1 = {'email':'benji@gmail.com','password':'bj_12345'}
		resp1 = self.app.post('/api/v1/user/signup', data=json.dumps(user1), content_type='application/json')
		self.assertEqual(resp1.status_code, 201)
		self.assertTrue('success' in json.loads(resp1.data)['status'])
		
	def test_login(self):
		user1 = {'email':'test@test.com','password':'12345678'}
		user2 = {'email':'bj@gmail.com','password':'12abdd'}
		resp1 = self.app.post('/api/v1/user/login', data=json.dumps(user1), content_type='application/json')
		resp2 = self.app.post('/api/v1/user/login', data=json.dumps(user2), content_type='application/json')
		self.assertEqual(resp1.status_code, 200)
		self.assertEqual(resp2.status_code, 403)
		self.assertTrue('access_token' in json.loads(resp1.data))
	
	
	def get_token(self):
		user = {'email':'test@test.com','password':'12345678'}
		resp = self.app.post('/api/v1/user/login', data=json.dumps(user), content_type='application/json')
		return json.loads(resp.data)['access_token']
		
	def create_employee(self):
		token = self.get_token()
		employee = {'first_name':'Abiola','last_name':'olu','age':44}
		resp = self.app.post('/api/v1/employee', data=json.dumps(employee),headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		return 'success'
	
		
	def test_add_employee(self):
		token = self.get_token()
		employee = {'first_name':'Abiola','last_name':'olu','age':44}
		resp = self.app.post('/api/v1/employee', data=json.dumps(employee),headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		self.assertEqual(resp.status_code, 201)
		self.assertTrue('success' in json.loads(resp.data)['status'])
		
	def test_get_employees(self):
		token = self.get_token()
		resp = self.app.get('/api/v1/employees',headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		self.assertEqual(resp.status_code,200)
		self.assertTrue('success' in json.loads(resp.data)['status'])
	
	
	def test_get_employee(self):
		token = self.get_token()
		self.create_employee()
		resp = self.app.get('/api/v1/employee/1',headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		
		
	def test_update_employee(self):
		token = self.get_token()
		self.create_employee()
		stats = {'age':45}
		resp1 = self.app.put('/api/v1/employee/2',data=json.dumps(stats),headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		resp2 = self.app.put('/api/v1/employee/1',data=json.dumps(stats),headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		self.assertEqual(resp1.status_code,404)
		self.assertTrue('Employee not found' in json.loads(resp1.data)['msg'])
		self.assertEqual(resp2.status_code,200)
		self.assertTrue('Update successful' in json.loads(resp2.data)['msg'])
		
		
	def test_delete_employee(self):
		token = self.get_token()
		self.create_employee()
		resp = self.app.delete('/api/v1/employee/1',headers={'Authorization':f'Bearer {token}'}, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('success' in json.loads(resp.data)['status'])
		
		
		
if __name__ == '__main__':
	unittest.main(verbosity=2)
