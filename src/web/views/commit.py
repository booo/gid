from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.views.auth.auth import *
from gid.Gid import Gid

@app.route('/repositories/<repo_name>/commits/<commit_sha>')
def commit(repo_name, commit_sha):
    commit = g.commit(repo_name, commit_sha)

    if "application/json" in request.headers['Accept']:
      return jsonify(commit=commit)
    else:
      return render_template('commit/show.html', commit = commit)
