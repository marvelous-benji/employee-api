from marshmallow import Schema, fields
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.orm import validates
import re
from employee_api import db


#creates user table
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), nullable=False, unique=True, index=True)
	password = db.Column(db.String(180), nullable=False)
	date_joined = db.Column(db.DateTime, default=datetime.now)
	employee = db.relationship('Employee', backref=db.backref('added_by'))
	
	
	@validates('email')
	def validate_email(self, key, email):
		if not re.match("[^@]+@[^@]+\.[^@]+", email):
			raise AssertionError('Provided email is not an email address')
		return email
		
	def create_user(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def hash_password(password):
		return sha256.hash(password)

	@staticmethod
	def verify_password(password,hash):
		return sha256.verify(password,hash)


	def __repr__(self):
		return f"User('{self.email}')"
	
#serialiser to convert user objects to json		
class UserSchema(Schema):
	class Meta:
		model = User
		sqla_session = db.session
		ordered = True
	id = fields.Integer(dump_only=True) #dump only the user id
		
#the employee table		
class Employee(db.Model):
	__tablename__ = 'employees'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(120),nullable=False, index=True)
	last_name = db.Column(db.String(120), nullable=False, index=True)
	age = db.Column(db.Integer, nullable=False)
	date_joined = db.Column(db.DateTime, default=datetime.now)
	last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	
	
	def create_employee(self):
		db.session.add(self)
		db.session.commit()
	
	
	def __repr__(self):
		return f"Employee('{self.first_name}','{self.last_name}')"
		
#employee serializer
class EmployeeSchema(Schema):
	class Meta:
		model = Employee
		sqla_session = db.session
		ordered = True
	id = fields.Integer(dump_only=True)
	first_name = fields.String(required=True)
	last_name = fields.String(required=True)
	age = fields.Integer(required=True)
	date_joined = fields.DateTime(dump_only=True)
	last_updated = fields.DateTime(dump_only=True)
	added_by = fields.Nested('UserSchema', only=('id',))

