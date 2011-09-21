import yaml

from flask import Flask, redirect, url_for, Response
from flaskext.sqlalchemy import SQLAlchemy

from werkzeug import url_decode

app = Flask(__name__)

stream = file('config/main.yaml', 'r')
app.config.update(yaml.load(stream))

db = SQLAlchemy(app)

# wsgi hook for lack of http methods
class MethodRewriteMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('__METHOD_OVERRIDE__')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)

app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)


import web.views.repository
import web.views.commit
import web.views.blob
import web.views.auth.user
import web.views.auth.session

@app.route('/static/css/<name>.sass')
def css(name):
   import os
   from scss import parser
   
   path = os.path.join(__name__, 'static', 'css', name) + '.sass'
   if os.path.exists(path):
      return Response(parser.load(path)) 

   return Response(""), 404

@app.route('/')
def index():
  return redirect(url_for('repos'))
