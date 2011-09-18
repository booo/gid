
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from rest_client import app


class UserAPI(MethodView):

    def get(self, username=None):
        pass


    #@normal_permission.require(http_exception=403)
    def put(self):
        pass


    def post(self):
        pass


    #@normal_permission.require(http_exception=403)
    def delete(self):
        raise NotYetImplemented()


app.add_url_rule('/users/',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET','PUT','POST'])
app.add_url_rule('/users/<username>',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET', 'DELETE'])


@app.route('/api/users/new')
def userNewForm():
    pass
