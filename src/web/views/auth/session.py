import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from restkit.errors import Unauthorized

from web import app
from web.models.rest import RestResource

from api.forms.login import LoginForm
from api.models.dictobject import DictObject
from api.forms.profile import ProfileForm


# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)


class SessionAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/session')


    @normal_permission.require(http_exception=403)
    def get(self):
        try :
            response = SessionAPI.rest.getWithAuth(
                  username = session['user.username'],
                  password = session['user.password']
              ) 
            
            form = ProfileForm(obj = DictObject(**json.loads(response)))

            return render_template('auth/profile.html', form=form)

        except Unauthorized:
            return redirect(url_for('login'))


    def post(self):
        form = LoginForm(request.form)

        if form.validate():

            try:
                response = self.rest.getWithAuth(
                      form.username.data,
                      form.password.data
                  ) 

                data = json.loads(response)

                identity = Identity(data['username'])
                identity_changed.send(app, identity=identity)

                session['user.username'] = data['username']
                session['user.password'] = form.password.data
                session['user.email'] = data['email']

                flash("Successfully logged in!", 'success')

                return redirect(url_for('session'))

            except Unauthorized:
                flash("Invalid credentials!", 'error')


        return render_template('auth/login.html', form=form)



    @normal_permission.require(http_exception=403)
    def delete(self):
        try:
            for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
                del session[key]

            for key in ['user.username', 'user.password', 'user.email']:
                del session[key]

        except KeyError:
            pass

        return redirect(url_for('login'))


app.add_url_rule('/session',
                 view_func=SessionAPI.as_view('session'),
                 methods=['GET','POST','DELETE'])


@app.route("/session/new")
def login():
    if 'identity.name' in session:
        redirect(url_for('session'))

    form = LoginForm(request.form)

    return render_template('auth/login.html', form=form)

@app.route("/session/destroy")
def destroy():
    return redirect(url_for('session') + '?__METHOD_OVERRIDE__=DELETE')
        
@app.errorhandler(403)
def page_not_found(e):
    session['redirected_from'] = request.url
    return redirect(url_for('login'))

    
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.provides.add(normal_role)
