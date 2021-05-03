from flask import jsonify, request
from employee_api import app, db, jwt
from flask_jwt_extended import create_access_token, current_user,jwt_required
from .models import User, Employee, EmployeeSchema




#This first two function helps in returning user object(from the database) so that i can make use of the current_user to access any authenticated user

@jwt.user_identity_loader
def user_identity_lookup(user):
	return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
	identity = jwt_data['sub']
	return User.query.filter_by(id=identity).one_or_none()








@app.route('/api/v1/')
def welcome_message():
	return jsonify('It works'), 200
	
	
@app.route('/api/v1/user/signup', methods=['POST'])
def user_signup():
	try:
		data = request.get_json()
		if User.query.filter_by(email=data['email']).first():
			#checks if email already exists and if email entered is valid(checks this through regex)
			return jsonify({'status':'failed','msg':'Email already exist'}), 400
		password = User.hash_password(data['password']) #hashes password to sha256 hash
		new_user = User(email=data['email'],password=password)
		new_user.create_user() # add user to database
		return jsonify({'status':'success','msg':'Account created successfully'}), 201
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'Input is invalid'}), 422
		
		
@app.route('/api/v1/user/login', methods=['POST'])
def user_login():
	try:
		data = request.get_json()
		user = User.query.filter_by(email=data['email']).first()
		if user and User.verify_password(data['password'],user.password):
			access_token = create_access_token(identity=user) #creates jwt tokens
			return jsonify({'status':'success','msg':'Login successfully','access_token':access_token}), 200
		return jsonify({'status':'failed','msg':'Invalid username or password'}), 403
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'Input is invalid'}), 422
	
		
@app.route('/api/v1/employee', methods=['POST'])
@jwt_required()
def add_employee():
	try:
		data = request.get_json()
		employee = Employee(first_name=data['first_name'],last_name=data['last_name'],
		age=data['age'], added_by=current_user)
		employee.create_employee()
		return jsonify({'status':'success','msg':'Employee added successfully'}), 201
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'Invalid input or required data is missing'}), 422
		
		

@app.route('/api/v1/employees', methods=['GET'])
@jwt_required()
def get_employees():
	try:
		employees = Employee.query.all()
		schema = EmployeeSchema(many=True)
		employees = schema.dump(employees)
		return jsonify({'status':'success','employees':employees}), 200
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'An unknown error occured'}), 500

		
@app.route('/api/v1/employee/<int:id>', methods=['GET'])
@jwt_required()
def get_employee(id):
	try:
		employee = Employee.query.filter_by(id=id).first()
		if employee:
			schema = EmployeeSchema()
			employee = schema.dump(employee)
			return jsonify({'status':'success','employee':employee}), 200
		return jsonify({'status':'failed','msg':f'Employee with id {id} not found'}), 404
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'An unknown error occured'}), 500
		
		
@app.route('/api/v1/employee/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
	try:
		data = request.get_json()
		employee = Employee.query.filter_by(id=id).first()
		if employee:
			if employee.added_by.id == current_user.id:
				#makes sure that only the user who added this employee can update it
				employee.first_name = data.get('first_name',employee.first_name)
				employee.last_name = data.get('last_name', employee.last_name)
				employee.age = data.get('age',employee.age)
				db.session.commit()
				schema = EmployeeSchema()
				employee = schema.dump(employee)
				return jsonify({'status':'success','msg':'Update successful','employee':employee}), 200
			return jsonify({'status':'failed','msg':'Operation not permitted'}), 401
		return jsonify({'status':'failed','msg':'Employee not found'}), 404
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'Invalid input'}), 422

		
@app.route('/api/v1/employee/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id):
	try:
		employee = Employee.query.filter_by(id=id).first()
		if employee:
			if employee.added_by.id == current_user.id:
				#ensures only users who added that employee could delete it
				db.session.delete(employee)
				db.session.commit()
				return jsonify({'status':'success','msg':'Employee deleted successful'}), 200
			return jsonify({'status':'failed','msg':'Operation not permitted'}), 401
		return jsonify({'status':'failed','msg':'Employee not found'}), 404
	except Exception as e:
		print(e)
		return jsonify({'status':'failed','msg':'Invalid input'}), 422
	
		
