from datetime import timedelta
from flask import Flask
import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS



app = Flask(__name__)
app.config['DEBUG'] = True
DATABASE_URL = os.environ['DB_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SECRET_KEY'] = os.getenv('SECRETS')
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_CREATE_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes=10)
CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
from employee_api import views


