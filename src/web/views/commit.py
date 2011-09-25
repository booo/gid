from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

from web.views.repository import  RepositoriesAPI, _dateInWords


@app.route('/repos/<username>/<repository>/commits')
def commitsByUserAndRepo(username, repository):
    urlRepo = '/%s/%s' % (username, repository)
    responseRepo = RepositoriesAPI.rest.get(
          urlRepo,
          headers = {'Accept': 'application/json'}
        ).body_string()
    repo = json.loads(responseRepo)['repo']

    amount = int(request.args.get('amount', 10))
    start = int(request.args.get('start', 0))

    urlCommits = '%s/commits' % urlRepo
    responseCommits = RepositoriesAPI.rest.get(
          urlCommits,
          headers = {'Accept': 'application/json'}
        ).body_string()
    commits = json.loads(responseCommits)['commits']

    for c in commits:
      c['date'] = _dateInWords(c['committer']['date'])

    tree = readmeSha = None
    if repo['git']['head'] != None:
      urlTree = '/%s/trees/%s' % (urlRepo, repo['git']['head']['tree'])
      response = RepositoriesAPI.rest.get(
          urlTree,
          recursive=0,
          headers = {'Accept': 'application/json'}
        ).body_string()
      tree = json.loads(response)['tree']

      readmeFile = filter((lambda x: 'README' in x['path']), tree)
      if len(readmeFile) > 0:
          readmeSha = readmeFile[0]['sha']

    def addDate(c):
        import pretty
        from datetime import datetime

        c['date'] = pretty.date(
          datetime.strptime(
            c['committer']['date'],
            '%Y-%m-%d %H:%M:%S'
          )
        )

    map(addDate, commits) 

    return render_template('commit/list.html', commits = commits, repo = repo,
    readmeSha = readmeSha)


@app.route('/repos/<username>/<repository>/commits/<sha>')
def commitByUserAndRepoAndSha(username, repository, sha):
    urlRepo = '/%s/%s' % (username, repository)
    responseRepo = RepositoriesAPI.rest.get(
          urlRepo,
          headers = {'Accept': 'application/json'}
        ).body_string()
    repo = json.loads(responseRepo)['repo']

    urlCommit = '/%s/commits/%s' % (urlRepo, sha)
    response = RepositoriesAPI.rest.get(
        urlCommit,
        headers = {'Accept': 'application/json'}
      ).body_string()
    commit = json.loads(response)['commit']

    urlTree = '/%s/trees/%s' % (urlRepo, commit['tree'])
    response = RepositoriesAPI.rest.get(
        urlTree,
        recursive=0,
        headers = {'Accept': 'application/json'}
      ).body_string()
    tree = json.loads(response)['tree']

    lexer = guess_lexer(commit['changes'])
    formatter = HtmlFormatter(linenos=True, noclasses=True)
    commit['changes'] = highlight(commit['changes'], lexer, formatter)

    commit['date'] = _dateInWords(commit['committer']['date'])
    
    return render_template('commit/show.html', 
              repo =repo, 
              commit = commit,
              tree = tree)
