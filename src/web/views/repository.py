from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.views.auth.session import *
from web.forms.repository import RepositoryForm
from web.models.repository import Repository

from gid.gitrepository import GitRepository

from flask.views import MethodView
class RepositoriesAPI(MethodView):

    def get(self, username):
        user = User.query.filter_by(username=username).first()
        
        repositories = []
        for repo in user.repositories:
            collaborators = []
            for collaborator in repo.collaborators: 
                if collaborator != repo.owner:
                  collaborators.append(collaborator.username)

            repositories.append({
                'name': repo.name,
                'description': repo.description,
                'owner': repo.owner.username,
                'collaborators': collaborators
              })

        data = {
          'user' : {
            'name': user.username,
            'email': user.email
          },
          'repositories': repositories
        }

        if "application/json" in request.headers['Accept']:
            return jsonify(data)
        else:
            return render_template('repository/list.html', user=data['user'], \
                                repositories=data['repositories'])

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

            db.session.add(repo) 
            db.session.commit()

            flash(u'Successfully created repository: ' + repoName, 'success')
            
            return redirect(url_for('repoShowByUserAndRepository',\
                              username = user.username,\
                              repository = repoName\
                           ))

        flash(u'Could not create repository:' + repoName, 'error')
        return render_template('repository/create.html', form=form,\
                                username=username)


    @normal_permission.require(http_exception=403)
    def put(self, username):
        pass

    @normal_permission.require(http_exception=403)
    def delete(self, username):
        pass

app.add_url_rule('/users/<username>/repositories/',\
                    view_func=RepositoriesAPI.as_view('repositories'))


@app.route('/users/<username>/repositories/create')
def repoCreateByUser(username):
    form = RepositoryForm(request.form)
    return render_template('repository/create.html', form=form,\
                                username=username)

@app.route('/users/<username>/repositories/<repository>')
def repoShowByUserAndRepository(username, repository):
    user = User.query.filter_by(username=username).first()
    repo = Repository.query.filter_by(name = repository, owner = user).first()
   
    data = {
      'name' : repo.name,
      'description' : repo.description,
      'owner' : {
        'name' : user.username,
        'email' : user.email,
      },
      'git' : GitRepository.show(repo.name, user.username) 
    }

    if "application/json" in request.headers['Accept']:
      return jsonify(data)
    else:
      return render_template('repository/show.html', repo = data)


@app.route('/users/<username>/repositories/<repository>/delete')
@normal_permission.require(http_exception=403)
def repoDeleteByUserAndRepository(username, repository):
  pass
