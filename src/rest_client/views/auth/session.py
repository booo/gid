import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from restclient import Resource

from rest_client import app

from rest_server.forms.login import LoginForm

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)

res  = Resource('http://127.0.0.1:5000/api/session')

class SessionAPI(MethodView):

    @normal_permission.require(http_exception=403)
    def get(self):
        pass

    def post(self):
        form = LoginForm(request.form)
        
        if form.validate():
          import urllib
          payload = 'username=%s&password=%s&csrf=%s' % (\
                       urllib.quote(form.username.data),
                       urllib.quote(form.password.data),
                       urllib.quote(form.csrf.data)
                     )

          print payload

          data = json.loads(res.post(
                '/',
                headers={'Content-Type':'application/x-www-form-urlencoded'},
                payload=payload
              )
            )

          return jsonify(data)

        return render_template('auth/login.html', form=form)



    @normal_permission.require(http_exception=403)
    def delete(self):
        pass

app.add_url_rule('/session/', view_func=SessionAPI.as_view('session'))


@app.route("/session/new")
def login():
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
