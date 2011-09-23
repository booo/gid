import shutil

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from api import app
from api.views.auth.session import *
from api.forms.repository import RepositoryForm
from api.models.repository import Repository
from api.models.dictobject import DictObject

from flask.views import MethodView

class RepositoriesAPI(MethodView):

    def get(self, username = None, reponame = None):
        # /repos => all public repositories
        if username == None:
            repos = [ 
              repo.toDict() 
              for repo in Repository.query.filter_by(private = False).all()
            ]

            return jsonify(repos=repos)

      # /repos/<username> => all repositories for user
        elif reponame == None:
            user = User.query.filter_by(username=username).first()
            repos = [ 
                repo.toDict() 
                for repo in Repository.query.filter_by(owner = user,
                  private=False).all()
              ]

            return jsonify(repos=repos)

      # /repos/<username>/<repository> => repository
        else:
          user = User.query.filter_by(username=username).first()
          repo = Repository.query.filter_by(name = reponame, owner = user).first()
         
          return jsonify(repo=repo.toDict())


    @requires_auth
    def post(self, username):
        form     = RepositoryForm(request.form, csrf_enabled = False)
        reponame = self._sanitize(form.name.data)

        if not 'private' in request.form or request.form['private'] == "False":
          form.private.data = False

        if form.validate():
            user = User.query.filter_by(username=session['identity.name']).first()

            if user.username == username:
                repo                  = Repository(reponame, user)
                repo.owner            = user
                repo.description      = form.description.data
                repo.private          = bool(form.private.data)
                repo.contributers     = [
                    User.query.filter_by(username=c).first()
                    for c in form.contributers.data.split(',')
                  ]

                db.session.add(repo) 
                db.session.commit()

                return jsonify(repo=repo.toDict())
          
        return jsonify({ 'error': form.errors})


    @requires_auth
    def put(self, username, reponame):
        form = RepositoryForm(request.form, csrf_enabled = False)

        if not 'private' in request.form or request.form['private'] == "False":
          form.private.data = False

        if form.validate():
            user                  = User.query.filter_by(username=username).first()
            repo                  = Repository.query.filter_by(name = reponame, owner = user).first()
            repo.name             = self._sanitize(form.name.data)
            repo.description      = form.description.data
            repo.private          = bool(form.private.data)


            def userForName(username):
                u = User.query.filter_by(username=username).first()
                if u != None:
                  return u
                return None

            repo.contributers     = map(
                    userForName,
                    [c for c in form.contributers.data.split(',')]
                )

            db.session.add(repo) 
            db.session.commit()

            if repo.name !=  reponame:
                shutil.move(
                  Repository._path(user.username, reponame),
                  Repository._path(user.username, repo.name)
                )

            return jsonify(repo=repo.toDict())
          
        return jsonifiy({ 'status':'invalid data'})



    @requires_auth
    def delete(self, username, reponame):
        user = User.query.filter_by(username = username).first()
        repo = Repository.query.filter_by(name = reponame, owner = user).first()

        if repo != None and repo.owner.username == session['identity.name']:

            shutil.rmtree(Repository._path(repo.owner.username, reponame))
            db.session.delete(repo)
            db.session.commit()


            return jsonify({'status':'success'})
          
        return jsonifiy({ 'status':'invalid data'})

      

    @staticmethod
    def _sanitize(value):
        import re
        return unicode(re.sub('[^\w]', '', value).strip())


app.add_url_rule('/api/repos',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET'])

app.add_url_rule('/api/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','POST'])
app.add_url_rule('/api/repos/<username>/<reponame>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','PUT','DELETE'])
