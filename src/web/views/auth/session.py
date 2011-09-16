from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web import app
from web.models.user import User, db
from web.forms.profile import ProfileForm
from web.forms.login import LoginForm

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

      return render_template('auth/profile.html', form=form)

    def post(self):
      form = LoginForm(request.form)
      if form.validate():
          username = request.form['username']
          password = request.form['password']        
          
          user = User.query.filter_by(username=username).first()

          if user:
            if user.password == password:
                identity = Identity(username)
                identity_changed.send(app, identity=identity)
                flash("Successfully logged in", "success")
                return redirect(url_for('session'))

      flash("log in failed", "error")
      return redirect(url_for('login'))


    @normal_permission.require(http_exception=403)
    def delete(self):
        for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
            try:
                del session[key]
            except:
                pass

        flash("Logged out", "success")

        return redirect(url_for('users'))

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