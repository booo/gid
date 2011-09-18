import shutil
import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from rest_client import app

from restclient import Resource

res  = Resource('http://127.0.0.1:5000/api')

from flask.views import MethodView

class RepositoriesAPI(MethodView):

    def get(self, username, reponame = None):
        if reponame == None:
          url = '/repos/%s' % username
          data = json.loads(res.get(url,headers={'Accept': 'application/json'}))

          return render_template('repository/listForUser.html',
                        username=username,
                        reponame = reponame,
                        repos=data['repos']
                 )

        else:
          url = '/repos/%s/%s' % (username, reponame)
          data = json.loads(res.get(url,headers={'Accept': 'application/json'}))

          return render_template('repository/show.html',
                        username=username,
                        reponame = reponame,
                        repo=data['repo']
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
    data = json.loads(res.get('/repos/',headers={'Accept': 'application/json'}))
    
    return render_template('repository/listAllRepositories.html', 
                      repos = data['repos'])


@app.route('/api/repos/<username>/new')
def repoNewForm(username):
    pass


@app.route('/api/repos/<username>/<repository>/edit')
def repoEditForm(username, repository):
    pass
