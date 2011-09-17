import shutil

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from rest_server import app
from rest_server.views.auth.session import *
from rest_server.forms.repository import RepositoryForm
from rest_server.models.repository import Repository
from rest_server.models.dictobject import DictObject

from flask.views import MethodView

class RepositoriesAPI(MethodView):

    def get(self, username, reponame = None):
        if reponame == None:
            user = User.query.filter_by(username=username).first()
            repos = [ 
                repo.toDict() 
                for repo in Repository.query.filter_by(owner = user).all()
              ]

            return jsonify(repos=repos)

        else:
          user = User.query.filter_by(username=username).first()
          repo = Repository.query.filter_by(name = reponame, owner = user).first()
         
          return jsonify(repo=repo.toDict())


    @normal_permission.require(http_exception=403)
    def post(self, username):
        form = RepositoryForm(request.form)
        reponame = form.name.data

        if form.validate():
            user = User.query.filter_by(username=session['identity.name']).first()

            if user.username == username:
                repo                  = Repository(reponame, user)
                repo.owner            = user
                repo.description      = form.description.data
                repo.private          = form.private.data
                repo.contributers    = [
                    User.query.filter_by(username=c).first()
                    for c in form.contributers.data.split(',')
                  ]

                db.session.add(repo) 
                db.session.commit()

                return jsonify(repo=repo.toDict())
          
        return jsonifiy({ 'status':'invalid data'})


    @normal_permission.require(http_exception=403)
    def put(self, username, reponame):
        form = RepositoryForm(request.form)

        if form.validate():
            user                  = User.query.filter_by(username=username).first()
            repo                  = Repository.query.filter_by(name = reponame, owner = user).first()
            repo.name             = form.name.data
            repo.description      = form.description.data
            repo.private          = form.private.data
            repo.contributers    = [
                User.query.filter_by(username=c).first()
                for c in form.contributers.data.split(',')
                if u != None
              ]

            db.session.add(repo) 
            db.session.commit()
            
            return jsonify(repo=repo.toDict())
          
        return jsonifiy({ 'status':'invalid data'})



    @normal_permission.require(http_exception=403)
    def delete(self, username, reponame):
        repo = Repository.query.filter_by(name = reponame).first()

        if repo.owner.username == session['identity.name']:

            shutil.rmtree(repo.path)
            db.session.delete(repo)
            db.session.commit()


            return jsonify({'status':'success'})
          
        return jsonifiy({ 'status':'invalid data'})

      

app.add_url_rule('/api/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','POST'])
app.add_url_rule('/api/repos/<username>/<reponame>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','PUT','DELETE'])


@app.route('/api/repos/')
def repoListPublic():
    repos = [ 
        repo.toDict() 
        for repo in Repository.query.filter_by(private = False).all()
      ]

    return jsonify(repos=repos)


@app.route('/api/repos/<username>/new')
def repoNewForm(username):
    form = RepositoryForm(request.form)
    return jsonify(form = form.toDict())


@app.route('/api/repos/<username>/<repository>/edit')
def repoEditForm(username, repository):
    user = User.query.filter_by(username=username).first()
    repo = Repository.query.filter_by(name = repository, owner = user).first()
    return jsonify(form = form.toDict())
