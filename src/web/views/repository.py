from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.views.auth.auth import *
from gid.Gid import Gid


@app.route('/')
def list():
    if "application/json" in request.headers['Accept']:
      return jsonify(repositories=Gid().list())
    else:
      return render_template('repository/list.html', repositories=Gid().list())

@app.route('/repositories/create', methods=['POST'])
@normal_permission.require(http_exception=403)
def create():
    try:
      name = Gid().create(request.form['repo'])[0]
      flash(u'Successfully created: ' + name, 'success')
    except OSError:
      flash(u'Error.', 'error')

    return redirect(url_for('list'))

@app.route('/repositories/<repo>/delete')
@normal_permission.require(http_exception=403)
def delete(repo):
    Gid().delete(repo)
    flash('Successfully deleted: ' + repo, 'success')

    return redirect(url_for('list'))

@app.route('/repositories/<repo>')
def show(repo):
    if "application/json" in request.headers['Accept']:
      return jsonify(repo=Gid().show(repo))
    else:
      return render_template('repository/show.html', repo=Gid().show(repo))

