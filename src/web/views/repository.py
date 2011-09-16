
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web import app
from web.views.auth.session import *
from web.forms.repository import RepositoryForm
from web.models.repository import Repository
from web.models.dictobject import DictObject

from gid.gitrepository import GitRepository
from gid.gitcommit import GitCommit

from flask.views import MethodView
class RepositoriesAPI(MethodView):

    def get(self, username):
        user = User.query.filter_by(username=username).first()
        repos = Repository.query.filter_by(owner = user).all()
            
        data = []
        for repo in repos:

            owner = {
              'id'   : repo.owner.id,
              'name' : repo.owner.username,
              'email': repo.owner.email
            }

            data.append({
                'id'          :   repo.id,
                'name'        : repo.name,
                'description' : repo.description,
                'owner'       : owner,
              }
            )

        if "application/json" in request.headers['Accept']:
          return jsonify(repositories=data)
        else:
          return render_template('repository/listForUser.html', repositories = data)

    @normal_permission.require(http_exception=403)
    def post(self, username):
        form = RepositoryForm(request.form)
        repoName = form.name.data

        if form.validate():
          user = User.query.filter_by(username=session['identity.name']).first()
          if user.username == username:
            repo = Repository(repoName, user)
            repo.owner = user
            repo.description = form.description.data
            repo.public = not form.private.data

            collaborators = []
            for collaborator in form.collaborators.data.split(','):
                c = User.query.filter_by(username=collaborator).first()
                collaborators.append(c)

            collaborators.append(repo.owner)
            repo.collaborators = collaborators

            db.session.add(repo) 
            db.session.commit()

            flash(u'Successfully created repository: ' + repoName, 'success')
            
            return redirect(url_for('repoShowByUserAndRepository',\
                              username = user.username,\
                              repository = repoName\
                           ))

        flash(u'Could not create repository:' + repoName, 'error')
        return render_template('repository/form.html', form=form,\
                                username=username,
                                submit='Create Repository')


    @normal_permission.require(http_exception=403)
    def put(self, username):
        form = RepositoryForm(request.form)
        repoName = form.name.data
        if form.validate():
            user = User.query.filter_by(username=username).first()
            repo = Repository.query.filter_by(name = repoName, owner = user).first()
            repo.name = repoName
            repo.description = form.description.data
            repo.public = not form.private.data

            repo.collaborators = [user]
            for c in form.collaborators.data.split(','):
                u = User.query.filter_by(username=c).first()
                if u != None:
                  repo.collaborators.append(u)

            db.session.add(repo) 
            db.session.commit()
            
            flash('Repository successfully edited', 'success')

            return redirect(url_for('repoShowByUserAndRepository',\
                                      username = user.username,\
                                      repository = repo.name))

        return Response("Error")



    @normal_permission.require(http_exception=403)
    def delete(self, username):
        pass

app.add_url_rule('/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repositories'))


@app.route('/repos/public')
def repoListIfPublic():
    repos = Repository.query.filter_by(public = True).all()

    data = []
    for repo in repos:

        owner = {
          'id'   : repo.owner.id,
          'name' : repo.owner.username,
          'email': repo.owner.email
        }

        data.append({
            'id'          :   repo.id,
            'name'        : repo.name,
            'description' : repo.description,
            'owner'       : owner,
          }
        )

    if "application/json" in request.headers['Accept']:
      return jsonify(repositories=data)
    else:
      return render_template('repository/listAllRepositories.html', repositories = data)




@app.route('/repos/<username>/new')
def repoCreateByUser(username):
    form = RepositoryForm(request.form)
    action = url_for('repositories', username=username)
    return render_template('repository/form.html', form=form,
                                username=username, action=action,
                                submit='Create Repository')

@app.route('/repos/<username>/<repository>/edit')
def repoEditByUserAndRepository(username, repository):
    user = User.query.filter_by(username=username).first()
    repo = Repository.query.filter_by(name = repository, owner = user).first()

    colls = []
    for c in repo.collaborators:
      if c != repo.owner:
        colls.append(c.username)

    obj = DictObject(\
      name = repo.name,\
      description = repo.description,\
      collaborators = ",".join(colls)\
    )

    form = RepositoryForm(obj = obj)
    action = url_for('repositories', username=username) +\
                        '?__METHOD_OVERRIDE__=PUT'
    return render_template('repository/form.html', form=form,\
                                username=username, action=action,\
                                submit='Edit Repository')

@app.route('/repos/<username>/<repository>')
def repoShowByUserAndRepository(username, repository):
    user = User.query.filter_by(username=username).first()
    repo = Repository.query.filter_by(name = repository, owner = user).first()
   
    collaborators = []
    for collaborator in repo.collaborators:
      if collaborator != user:
        collaborators.append(collaborator.username)

    data = {
      'name' : repo.name,
      'description' : repo.description,
      'owner' : {
        'name' : user.username,
        'email' : user.email,
      },
      'collaborators': collaborators,
      'git' : GitRepository.show(repo.name, user.username) 
    }

    if "application/json" in request.headers['Accept']:
      return jsonify(data)
    else:
      commits = GitCommit.list(repository, username)
      return render_template('repository/show.html', repo = data, \
                                commits = commits, owner = username,\
                                repository = repo.name)


@app.route('/repos/<username>/<repository>/delete')
@normal_permission.require(http_exception=403)
def repoDeleteByUserAndRepository(username, repository):
  pass
