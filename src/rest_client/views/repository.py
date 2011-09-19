import shutil
import json

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flaskext.principal import Identity, Principal, RoleNeed, UserNeed, \
            Permission, identity_changed, identity_loaded

from flask.views import MethodView

from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

from restclient import Resource
from restkit.errors import Unauthorized
from rest_client import app
from rest_client.models.rest import RestResource
from rest_client.views.auth.session import normal_permission
from rest_server.forms.repository import RepositoryForm
from rest_server.models.dictobject import DictObject


class RepositoriesAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/repos')

    def get(self, username = None, reponame = None):
        if username == None:

            response = RepositoriesAPI.rest.get(
                headers = {'Accept': 'application/json'}
              ).body_string()

            repos = json.loads(response)['repos']
            
            return render_template('repository/listAllRepositories.html', 
                      repos = repos)

        elif reponame == None:
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

            tree = readme = None
            if repo['git']['head'] != None:
              urlTree = '/%s/trees/%s' % (urlRepo, repo['git']['head']['tree'])
              response = RepositoriesAPI.rest.get(
                  urlTree,
                  recursive=1,
                  headers = {'Accept': 'application/json'}
                ).body_string()
              tree = json.loads(response)['tree']

              readmeFile = filter((lambda x: 'README' in x['path']), tree)
              if len(readmeFile) > 0:
                  urlBlob = '/%s/blobs/%s' % (urlRepo, readmeFile[0]['sha'])
                  response = RepositoriesAPI.rest.get(
                      urlBlob,
                      headers = {'Accept': 'application/json'}
                    ).body_string()
                  blob = json.loads(response)['blob']

                  blob['content'] = "".join(blob['content'])

                  lexer = guess_lexer(blob['content'])
                  formatter = HtmlFormatter(noclasses=True)
                  readme = highlight(blob['content'], lexer, formatter)


            return render_template('repository/show.html',
                          username=username,
                          reponame = reponame,
                          repo=repo,
                          commits=commits,
                          tree = tree,
                          readme = readme
                   )


    @normal_permission.require(http_exception=403)
    def post(self, username):
        form = RepositoryForm(request.form)

        if form.validate():
            response = self.rest.postForm(
                  form.toDict(),
                  '/%s' % username,
                  {app.session_cookie_name : session.serialize()}
              ) 

            data = json.loads(response)

            flash("Repository created!", "success")

            return redirect(url_for('repos', 
                        username=username,
                        reponame=form.name.data
                      )
                    )

        action = url_for('repos', username=username)
        return render_template('repository/form.html', form=form,
                                    username=username, action=action,
                                    submit='Create Repository')




    @normal_permission.require(http_exception=403)
    def put(self, username, reponame):
        form = RepositoryForm(request.form)

        print request.form
        print form.toDict()['private']

        if form.validate():
            response = self.rest.putForm(
                  form.toDict(),
                  '/%s/%s' % (username, reponame),
                  {app.session_cookie_name : session.serialize()}
              ) 

            repo = json.loads(response)['repo']

            flash('Repository successfully edited', 'success')

            return redirect(url_for('repos',
                                      username = repo['owner']['username'],
                                      reponame = repo['name']))


        action = url_for('repos', username=username, reponame = reponame) +\
                            '?__METHOD_OVERRIDE__=PUT'
        return render_template('repository/form.html', form=form,
                                    username=username, action=action,
                                    submit='Edit Repository')


    @normal_permission.require(http_exception=403)
    def delete(self, username, reponame):
        if username == session['identity.name']:
            try:
                response = RepositoriesAPI.rest.deleteWithCookie(
                    {app.session_cookie_name : session.serialize()},
                    '/%s/%s' % (username, reponame)
                  )

                flash("Successfully deleted: " + reponame)

                return redirect(url_for('repos', username = username))

            except Unauthorized:
                flash("Unauthorized", "error"), 401

        return redirect(url_for('repos', username = username,reponame=reponame))


app.add_url_rule('/repos',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET'])
app.add_url_rule('/repos/<username>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','POST'])
app.add_url_rule('/repos/<username>/<reponame>',\
                    view_func=RepositoriesAPI.as_view('repos'),
                    methods=['GET','PUT','DELETE'])


@app.route('/repos/<username>/new')
def repoNewForm(username):
    form = RepositoryForm(request.form)
    action = url_for('repos', username=username)
    return render_template('repository/form.html', form=form,
                                username=username, action=action,
                                submit='Create Repository')


@app.route('/repos/<username>/<reponame>/edit')
def repoEditForm(username, reponame):
    urlRepo = '/%s/%s' % (username, reponame)
    responseRepo = RepositoriesAPI.rest.get(
          urlRepo,
          headers = {'Accept': 'application/json'}
        ).body_string()

    repo = json.loads(responseRepo)['repo']

    obj = DictObject(**repo)
    obj.contributers = ",".join(c['username'] for c in repo['contributers'])

    form = RepositoryForm(obj = obj)
    action = url_for('repos', username=username, reponame = repo['name']) +\
                        '?__METHOD_OVERRIDE__=PUT'
    return render_template('repository/form.html', form=form,\
                                username=username, action=action,\
                                submit='Edit Repository')
