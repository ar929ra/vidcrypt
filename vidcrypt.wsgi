import sys

sys.path.insert(0,"/var/www/vidcrypt/")

from vidcrypt import app as application
application.secret_key = '5791628bb0b13ce0c676dfde280ba245'
