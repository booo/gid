from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.views.auth.auth import *
from gid.Gid import Gid

g = Gid()

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