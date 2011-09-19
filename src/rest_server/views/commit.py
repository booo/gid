from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from rest_server import app
from rest_server.models.repository import Repository
from rest_server.models.user import User

@app.route('/api/repos/<username>/<repository>/commits')
def commitsByUserAndRepo(username, repository):
    user = User.query.filter_by(username = username).first()
    repo = Repository.query.filter_by(owner = user, name = repository).first()
    amount = int(request.args.get('amount', 0)) or None
    commits = [c for c in repo.git.getCommits(amount)] 

    return jsonify(commits=commits)


@app.route('/api/repos/<username>/<repository>/commits/<sha>')
def commitByUserAndRepoAndSha(username, repository, sha):
    user = User.query.filter_by(username = username).first()
    repo = Repository.query.filter_by(owner = user, name = repository).first()

    return jsonify(commit=repo.git.getCommit(sha))
