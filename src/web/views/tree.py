from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from web.views.repository import  RepositoriesAPI

@app.route('/repos/<username>/<repository>/trees/<sha>')
def treeByUserAndRepoAndSha(username, repository, sha):
    urlRepo = '/%s/%s' % (username, repository)
    responseRepo = RepositoriesAPI.rest.get(
          urlRepo,
          headers = {'Accept': 'application/json'}
        ).body_string()
    repo = json.loads(responseRepo)['repo']

    urlTree = '/%s/trees/%s' % (urlRepo, sha)
    response = RepositoriesAPI.rest.get(
        urlTree,
        recursive=0,
        headers = {'Accept': 'application/json'}
      ).body_string()
    tree = json.loads(response)['tree']

    return render_template('tree/_show.html', tree = tree, repo = repo)
