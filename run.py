from employee_api import app, db
from flask_migrate import Migrate
from employee_api.models import User



migrate = Migrate(app,db)



@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User)


if __name__ == '__main__':
	app.run()
