from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from web.views.repository import  RepositoriesAPI


@app.route('/repos/<username>/<repository>/blobs/<sha>')
def blobByUserAndRepoAndSha(username, repository, sha):
    urlRepo = '/%s/%s' % (username, repository)
    responseRepo = RepositoriesAPI.rest.get(
          urlRepo,
          headers = {'Accept': 'application/json'}
        ).body_string()
    repo = json.loads(responseRepo)['repo']

    urlBlob = '/%s/blobs/%s' % (urlRepo, sha)
    response = RepositoriesAPI.rest.get(
        urlBlob,
        headers = {'Accept': 'application/json'}
      ).body_string()
    blob = json.loads(response)['blob']

    blob['content'] = "".join(blob['content'])
    blob['sha'] = "".join(blob['sha'])

    lexer = guess_lexer(blob['content'])
    formatter = HtmlFormatter(linenos=True, noclasses=True)
    blob['content'] = highlight(blob['content'], lexer, formatter)

    standalone = request.args.get('standalone', False)

    return render_template('blob/show.html', 
              repo =repo, 
              blob = blob,
              standalone = standalone)

