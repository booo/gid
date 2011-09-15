from flask import Flask
from web.models.user import User, db


app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'algjsgASKSAGs72385hbq1bnaskghJSGSGASGjkjk898909'
)


# create some users
#users = [User("user" + str(id), "user@"+str(id)) for id in range(1, 21)]
#for user in users:
#  db.session.add(user)
#db.session.commit()


# views
from web.views.views import *
