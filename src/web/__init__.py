from flask import Flask
from user import User


app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'algjsgASKSAGs72385hbq1bnaskghJSGSGASGjkjk898909'
)


# create some users
users = [User(id) for id in range(1, 21)]

# views
import web.views
