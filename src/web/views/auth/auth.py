from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.models.user import User, db
from web.forms.registration import RegistrationForm
from web.forms.login import LoginForm

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)

# somewhere to login
@app.route("/user/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']        
        
        user = User.query.filter_by(username=username).first()
        if user:
          if user.password == password:
              identity = Identity(username)
              identity_changed.send(app, identity=identity)
              flash("Successfully logged in", "success")
              return redirect(url_for('list'))
          else:
              flash("log in failed", "error")

    return render_template('login.html', form=form)


# somewhere to logout
@app.route("/user/logout")
@normal_permission.require(http_exception=403)
def logout():
    for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
        try:
            del session[key]
        except:
            pass

    flash("Logged out")
    return redirect(url_for('list'))


@app.route('/user/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():

      if not User.query.filter_by(username = form.username.data).count() > 0:
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('list'))

      else:
          flash("Username already exist", "error")
    return render_template('register.html', form=form)


@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
     
        
@app.errorhandler(403)
def page_not_found(e):
    session['redirected_from'] = request.url
    return redirect(url_for('login'))

    
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.provides.add(normal_role)
