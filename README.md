# vidcrypt
Repository for the OSU SE I class project

To run locally:

Install the necessary packages

pip install flask flask_sqlalchemy flask_bcrypt flask_httpauth flask_login

Run python from the vidcrypt directory and do the following

> from vidcrypt import db
> db.create_all()

> from vidcrypt import app
> app.run('0.0.0.0')
