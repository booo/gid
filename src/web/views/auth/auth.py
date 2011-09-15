from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.models.user import User, db
from web.forms.registration import RegistrationForm
from web.forms.login import LoginForm
from web.forms.profile import ProfileForm

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)

@app.route("/users")
def userList():
  users = []
  for user in User.query.all():
    data = {
      'name' : user.username,
      'email' : user.email
    }
    users.append(data)
  
  if "application/json" in request.headers['Accept']:
    return jsonify(users = AndShausers)
  else:
    return render_template('auth/users.html', users=users)

# somewhere to login
@app.route("/users/login", methods=["GET", "POST"])
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
              return redirect(url_for('userList'))
              #return Response("Logged in")
          else:
              flash("log in failed", "error")

    return render_template('auth/login.html', form=form)


# somewhere to logout
@app.route("/users/logout")
@normal_permission.require(http_exception=403)
def logout():
    for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
        try:
            del session[key]
        except:
            pass

    flash("Logged out", "success")
    #return Response("Logged out")
    return redirect(url_for('userList'))


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():

      if not User.query.filter_by(username = form.username.data).count() > 0:
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering',"success")
        return redirect(url_for('userList'))
        #return Response("Registered in")

      else:
          flash("Username already exist", "error")
    return render_template('auth/register.html', form=form)


@app.route("/users/profile", methods=['GET', 'POST'])
@normal_permission.require(http_exception=403)
def profile():
    if request.method == 'POST':
      form = ProfileForm(request.form)
      if form.validate():
        user = User.query.filter_by(username = session['identity.name']).first()
        user.username = form.username.data 
        user.email = form.email.data 
        user.key = form.key.data 
        
        db.session.add(user)
        db.session.commit()

        flash("Updated profile informations", "success")

    else:
      user = User.query.filter_by(username = session['identity.name']).first()

      form = ProfileForm(obj = user)

    return render_template('auth/profile.html', form=form)



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
