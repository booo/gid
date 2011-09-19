from flask import Flask, request, render_template, json, \
                               flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from rest_server import app
from rest_server.models.user import User, db
from rest_server.forms.profile import ProfileForm
from rest_server.forms.login import LoginForm

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)

class SessionAPI(MethodView):

    @normal_permission.require(http_exception=403)
    def get(self):
        user = User.query.filter_by(username = session['identity.name']).first()
        form = ProfileForm(obj = user)

        return jsonify(form.toDict())

    def post(self):

        form = LoginForm(obj = request.form)

        print form.toDict()

        if form.validate():

            username = form.username.data
            password = form.password.data
            
            user = User.query.filter_by(username=username).first()

            if user:
              if user.password == password:
                  identity = Identity(username)
                  identity_changed.send(app, identity=identity)

                  return jsonify(form.toDict())

              else:
                  return jsonify({'errors' : 'invalid credentials' }), 401

        return jsonify( form.errors ), 401


    @normal_permission.require(http_exception=403)
    def delete(self):
        try:
            for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
                del session[key]
            return jsonify({ 'status':'ok'})

        except KeyError:
            return jsonify({ 'status':'invalid data'})

app.add_url_rule('/api/session',
                 view_func=SessionAPI.as_view('session'),
                 methods=['GET','POST','DELETE'])


@app.route("/api/session/new")
def login():
    form = LoginForm(request.form)

    return jsonify(form=form.toDict())

@app.errorhandler(403)
def page_not_found(e):
    return Response(""), 401

    
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.provides.add(normal_role)
