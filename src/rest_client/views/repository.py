import shutil
import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from rest_client import app
from rest_client.models.rest import RestResource

from restclient import Resource

from flask.views import MethodView

class RepositoriesAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/repos')

    def get(self, username, reponame = None):
        if reponame == None:
            url = '/%s' % username
            response = RepositoriesAPI.rest.get(
                  url,
                  headers = {'Accept': 'application/json'}
                ).body_string()

            repos = json.loads(response)['repos']

            return render_template('repository/listForUser.html',
                          username=username,
                          reponame = reponame,
                          repos=repos
                   )

        else:
            urlRepo = '/%s/%s' % (username, reponame)
            responseRepo = RepositoriesAPI.rest.get(
                  urlRepo,
                  headers = {'Accept': 'application/json'}
                ).body_string()
            repo = json.loads(responseRepo)['repo']

            urlCommits = '%s/commits' % urlRepo
            responseCommits = RepositoriesAPI.rest.get(
                  urlCommits,
                  headers = {'Accept': 'application/json'}
                ).body_string()
            commits = json.loads(responseCommits)['commits']

            return render_template('repository/show.html',
                          username=username,
                          reponame = reponame,
                          repo=repo,
                          commits=commits
                   )






    #@normal_permission.require(http_exception=403)
    def post(self, username):
        pass

    #@normal_permission.require(http_exception=403)
    def put(self, username, reponame):
        pass


    #@normal_permission.require(http_exception=403)
    def delete(self, username, reponame):
        pass


app.add_url_rule('/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','POST'])
app.add_url_rule('/repos/<username>/<reponame>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','PUT','DELETE'])


@app.route('/repos/')
def repoListPublic():
    response = RepositoriesAPI.rest.get(
        '/',
        headers = {'Accept': 'application/json'}
      ).body_string()

    repos = json.loads(response)['repos']
    
    return render_template('repository/listAllRepositories.html', 
                      repos = repos)


@app.route('/api/repos/<username>/new')
def repoNewForm(username):
    pass


@app.route('/api/repos/<username>/<repository>/edit')
def repoEditForm(username, repository):
    pass
