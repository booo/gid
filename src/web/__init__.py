from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'algjsgASKSAGs72385hbq1bnaskghJSGSGASGjkjk898909',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../../data/db/sqlite.db'
)

db = SQLAlchemy(app)

# views
import web.views.commit
import web.views.repository
