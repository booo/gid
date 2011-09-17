from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from rest_server import app
from rest_server.models.repository import Repository
from rest_server.models.user import User

@app.route('/api/repos/<username>/<repository>/blobs/<sha>')
def BlobByUserAndRepoAndSha(username, repository, sha):
    user = User.query.filter_by(username = username).first()
    repo = Repository.query.filter_by(owner = user, name = repository).first()

    return jsonify(blob=repo.git.getBlob(sha))
