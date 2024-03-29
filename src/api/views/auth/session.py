from flask import Flask, request, render_template, json, \
                               flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from api import app
from api.models.user import User, db
from api.forms.profile import ProfileForm
from api.forms.login import LoginForm


from functools import wraps
from flask import request, Response


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """

    user          = User.query.filter_by(
                      username = username 
                    ).first()

    import hashlib
    if user != None:
      if user.password == hashlib.sha1(password).hexdigest()\
        or user.token == password:
        return True

    return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()


        session['identity.name'] = auth.username
        return f(*args, **kwargs)
    return decorated


class SessionAPI(MethodView):

    @requires_auth
    def get(self):
        user = User.query.filter_by(username = session['identity.name']).first()
        form = ProfileForm(obj = user)

        return jsonify(form.toDict())


app.add_url_rule('/api/session',
                 view_func=SessionAPI.as_view('session'),
                 methods=['GET'])
