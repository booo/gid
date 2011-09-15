import yaml

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

stream = file('config/main.yaml', 'r')
app.config.update(yaml.load(stream))

db = SQLAlchemy(app)

# views
import web.views.commit
import web.views.repository
