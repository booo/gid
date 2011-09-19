from rest_client import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

@app.route('/users/<username>/repositories/<repository>/commits')
def commitsByUserAndRepo(username, repository):
    
    #data = json.loads(res.get('/repos/',headers={'Accept': 'application/json'}))

    return render_template('commit/list.html', \
              repository = data['repository'], \
              owner = data['owner'],\
              commits = data['commits'])

@app.route('/users/<username>/repositories/<repository>/commits/<sha>')
def commitByUserAndRepoAndSha(username, repository, sha):
    return render_template('commit/show.html', repo=repository,\
                                  user=username, commit = commit)

