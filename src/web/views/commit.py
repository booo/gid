from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from gid.gitcommit import GitCommit

@app.route('/users/<username>/repositories/<repository>/commits')
def commitsByUserAndRepo(username, repository):

    commits = GitCommit.list(repository, username)

    data = {
      "repository" : repository,
      "owner" : username,
      "commits": commits
    }

    if "application/json" in request.headers['Accept']:
      return jsonify(data)
    else:
      return render_template('commit/list.html', \
                repository = data['repository'], \
                owner = data['owner'], \
                commits = data['commits'])

@app.route('/users/<username>/repositories/<repository>/commits/<sha>')
def commitByUserAndRepoAndSha(username, repository, sha):
    commit = GitCommit.show(repository, username, sha)

    if "application/json" in request.headers['Accept']:
      return jsonify(commit=commit)
    else:
      return render_template('commit/show.html', commit = commit)
