from web import app
from user import User, db

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from gid.Gid import Gid


g = Gid()

# flask-principal
principals = Principal()
normal_role = RoleNeed('normal')
normal_permission = Permission(normal_role)
principals._init_app(app)

# somewhere to login
@app.route("/user/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            identity = Identity(username)
            identity_changed.send(app, identity=identity)
            flash("Successfully logged in", "success")
        else:
            flash("log in failed", "error")

    return redirect(url_for('list'))


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

@app.route("/user/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['username']
      email = request.form['email']

      if not User.query.filter_by(username=username).count() > 0:
          user = User(username, password, email)

          db.session.add(user)
          db.session.commit()

          flash("Successfully registered!", "success")

          return redirect(url_for('list'))

      else:
          flash("Username already exist", "error")

    return render_template('register.html')


@app.route('/')
def list():
    if "application/json" in request.headers['Accept']:
      return jsonify(repos=g.list())
    else:
      return render_template('list.html', repos=g.list())

@app.route('/repository/create', methods=['POST'])
@normal_permission.require(http_exception=403)
def create():
    try:
      name = g.create(request.form['repo'])[0]
      flash(u'Successfully created: ' + name, 'success')
    except OSError:
      flash(u'Error.', 'error')

    return redirect(url_for('list'))

@app.route('/repository/<repo>/delete')
@normal_permission.require(http_exception=403)
def delete(repo):
    g.delete(repo)
    flash('Successfully deleted: ' + repo, 'success')

    return redirect(url_for('list'))

@app.route('/repository/<repo>')
def view(repo):
    if "application/json" in request.headers['Accept']:
      return jsonify(repo=g.detail(repo))
    else:
      return render_template('detail.html', repo=g.detail(repo))

@app.route('/repository/<repo_name>/commit/<commit_sha>')
def commit(repo_name, commit_sha):
    commit = g.commit(repo_name, commit_sha)

    if "application/json" in request.headers['Accept']:
      return jsonify(commit=commit)
    else:
      return render_template('commit.html', commit = commit)


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
