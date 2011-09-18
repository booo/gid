import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded


from rest_client import app
from rest_client.models.rest import RestResource

from rest_server.forms.login import LoginForm

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)


class SessionAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/session')


    @normal_permission.require(http_exception=403)
    def get(self):
        pass

    def post(self):
        form = LoginForm(request.form)
        
        print "POST - proxy: " + str(session['proxy'])

        if form.validate():
          data =  {
              'username' : form.username.data,
              'password' : form.password.data,
              'csrf'     : form.csrf.data
            }

          response, session['proxy'] = self.rest.postForm(
                '/',
                data,
                {app.session_cookie_name : session.serialize()}
            ) 

          return jsonify(json.loads(response))

        return render_template('auth/login.html', form=form)



    @normal_permission.require(http_exception=403)
    def delete(self):
        response, session['proxy'] = self.rest.deleteWithCookie('/',session.get('proxy', None)) 

        return redirect(url_for('login'))


app.add_url_rule('/session/', view_func=SessionAPI.as_view('session'))


@app.route("/session/new")
def login():
    if 'identity.name' in session:
        redirect(url_for('session'))

    response, proxy = SessionAPI.rest.getWithCookies(
          '/new',
          {app.session_cookie_name : session.serialize()}
      ) 


    data = json.loads(response)

    request.form.csrf = data['form']['csrf']
    
    form = LoginForm(request.form)

    print "GET - session: " + session.serialize().split("?",1)[0]
    print "GET - csrf: " + form.csrf.data 

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
