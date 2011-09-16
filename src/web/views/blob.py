from web import app

from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

from gid.gitblob import GitBlob

@app.route('/users/<username>/repositories/<repository>/blobs/<sha>')
def BlobByUserAndRepoAndSha(username, repository, sha):
    blob = GitBlob.show(repository, username, sha)

    if "application/json" in request.headers['Accept']:
      return jsonify(blob=blob)
    else:
      lexer = guess_lexer(blob["content"])
      formatter = HtmlFormatter(linenos=True, noclasses=True)
      blob["content"] = highlight(blob["content"], lexer, formatter)

      return render_template('blob/show.html', blob=blob)
