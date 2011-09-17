
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

    def get(self, username, reponame = None):
        if reponame == None:

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

        else:

          user = User.query.filter_by(username=username).first()
          repo = Repository.query.filter_by(name = reponame, owner = user).first()
         
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
            commits = GitCommit.list(reponame, username)
            return render_template('repository/show.html', repo = data, \
                                      commits = commits, owner = username,\
                                      repository = repo.name)


    @normal_permission.require(http_exception=403)
    def post(self, username):
        form = RepositoryForm(request.form)
        reponame = form.name.data

        if form.validate():
          user = User.query.filter_by(username=session['identity.name']).first()
          if user.username == username:
            repo = Repository(reponame, user)
            repo.owner = user
            repo.description = form.description.data
            repo.private = form.private.data

            collaborators = []
            for collaborator in form.collaborators.data.split(','):
                c = User.query.filter_by(username=collaborator).first()
                collaborators.append(c)

            collaborators.append(repo.owner)
            repo.collaborators = collaborators

            db.session.add(repo) 
            db.session.commit()

            flash(u'Successfully created repository: ' + reponame, 'success')
            
            return redirect(url_for('repos',\
                              username = user.username,\
                              reponame = reponame\
                           ))

        flash(u'Could not create repository:' + reponame, 'error')
        return render_template('repository/form.html', form=form,\
                                username=username,
                                submit='Create Repository')


    @normal_permission.require(http_exception=403)
    def put(self, username):
        form = RepositoryForm(request.form)
        reponame = form.name.data

        if form.validate():
            user = User.query.filter_by(username=username).first()
            repo = Repository.query.filter_by(name = reponame, owner = user).first()
            repo.name = reponame
            repo.description = form.description.data
            repo.private = form.private.data
            
            repo.collaborators = [user]
            for c in form.collaborators.data.split(','):
                u = User.query.filter_by(username=c).first()
                if u != None:
                  repo.collaborators.append(u)

            db.session.add(repo) 
            db.session.commit()
            
            flash('Repository successfully edited', 'success')

            return redirect(url_for('repos',\
                                      username = user.username,\
                                      reponame = repo.name))

        return Response("Error")



    @normal_permission.require(http_exception=403)
    def delete(self, username, reponame):
        repo = Repository.query.filter_by(name = reponame).first()
        if repo.owner.username == session['identity.name']:
          db.session.delete(repo)
          db.session.commit()
          GitRepository.delete(reponame, username)

          flash("Successfully deleted: " + reponame)

        else:
          flash("Unauthorized", "error")

        return redirect(url_for('repos', username = username))

      

app.add_url_rule('/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','PUT','POST'])
app.add_url_rule('/repos/<username>/<reponame>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET', 'DELETE'])


@app.route('/repos/public')
def repoListPublic():
    repos = Repository.query.filter_by(private = False).all()

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
def repoNewForm(username):
    form = RepositoryForm(request.form)
    action = url_for('repos', username=username)
    return render_template('repository/form.html', form=form,
                                username=username, action=action,
                                submit='Create Repository')

@app.route('/repos/<username>/<repository>/edit')
def repoEditForm(username, repository):
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
    action = url_for('repos', username=username) +\
                        '?__METHOD_OVERRIDE__=PUT'
    return render_template('repository/form.html', form=form,\
                                username=username, action=action,\
                                submit='Edit Repository')
