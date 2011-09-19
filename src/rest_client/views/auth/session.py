import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from restkit.errors import Unauthorized

from rest_client import app
from rest_client.models.rest import RestResource

from rest_server.forms.login import LoginForm
from rest_server.models.dictobject import DictObject
from rest_server.forms.profile import ProfileForm


# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)


class SessionAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/session')


    @normal_permission.require(http_exception=403)
    def get(self):
        response = SessionAPI.rest.getWithCookies(
              '/',
              {app.session_cookie_name : session.serialize()}
          ) 
        
        form = ProfileForm(obj = DictObject(**json.loads(response)))

        return render_template('auth/profile.html', form=form)


    def post(self):
        form = LoginForm(request.form)


        if form.validate():

            try:
                response = self.rest.postForm(
                      '/',
                      form.toDict(),
                      {app.session_cookie_name : session.serialize()}
                  ) 

                data = json.loads(response)

                if 'username' in data and data['username'] != None:
                    identity = Identity(data['username'])
                    identity_changed.send(app, identity=identity)

                    return redirect(url_for('session'))

            except Unauthorized:
                flash("Invalid credentials!", 'error')


        return render_template('auth/login.html', form=form)



    @normal_permission.require(http_exception=403)
    def delete(self):
        response = self.rest.deleteWithCookie(
                        '/',
                        {app.session_cookie_name : session.serialize()}
                      )

        try:
            for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
                del session[key]

        except KeyError:
            pass

        return redirect(url_for('login'))


app.add_url_rule('/session', view_func=SessionAPI.as_view('session'))


@app.route("/session/new")
def login():
    if 'identity.name' in session:
        redirect(url_for('session'))

    response = SessionAPI.rest.getWithCookies(
          '/new',
          {app.session_cookie_name : session.serialize()}
      ) 


    data = json.loads(response)

    session['_csrf_token'] = data['form']['csrf']
    request.form.csrf = data['form']['csrf']
    
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
