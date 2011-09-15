from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from web.views.auth.auth import *
from web.forms.repository import RepositoryForm
from web.models.repository import Repository

from gid.gitrepository import GitRepository


@app.route('/users/<username>/repositories')
def repoListByUser(username):
    user = User.query.filter_by(username=username).first()
    
    repositories = []
    for repo in user.repositories:
      repositories.append({
          'name': repo.name,
          'description': repo.description
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

@app.route('/users/<username>/repositories/create', methods=['GET', 'POST'])
@normal_permission.require(http_exception=403)
def repoCreateByUser(username):
    form = RepositoryForm(request.form)

    if request.method == 'POST' and form.validate():
      user = User.query.filter_by(username=session['identity.name']).first()
      if user.username == username:
        repoName = form.name.data

        repo = Repository(repoName, user)
        repo.owner = user

        db.session.add(repo) 
        db.session.commit()

        flash(u'Successfully created repository: ' + repoName, 'success')

    return render_template('repository/create.html', form=form,
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
