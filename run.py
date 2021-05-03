from employee_api import app, db
from flask_migrate import Migrate
from employee_api.models import User

#this is the file that starts the application
#needed for database migration
migrate = Migrate(app,db)


#needed to directly interact with the database objects in python object format
@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User)


if __name__ == '__main__':
	app.run()
