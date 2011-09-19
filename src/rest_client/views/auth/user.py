
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from rest_client import app
from rest_client.models.rest import RestResource
from rest_client.views.auth.session import normal_permission

from rest_server.forms.profile import ProfileForm
from rest_server.forms.registration import RegistrationForm
from rest_server.models.dictobject import DictObject

class UserAPI(MethodView):

    rest = RestResource('http://127.0.0.1:5000/api/users')

    def get(self, username):
        url = '/%s' % username
        try: 
          response = UserAPI.rest.get(
                url,
                headers = {'Accept': 'application/json'}
              ).body_string()

          user = json.loads(response)['user']

          return render_template('auth/user.html',
                        user=user
                 )
        except ResourceNotFound:
          pass

        return Response(""), 404


    @normal_permission.require(http_exception=403)
    def put(self):
        form = ProfileForm(request.form)

        if form.validate():
            response = self.rest.putForm(
                  form.toDict(),
                  {app.session_cookie_name : session.serialize()}
              ) 

            data = json.loads(response)

            flash("Successfully updated your profile!", "success")


        #form = ProfileForm(obj = DictObject(**json.loads(response)))

        return render_template('auth/profile.html', form=form)


    def post(self):
        form = RegistrationForm(request.form)

        if form.validate():

            response = self.rest.postForm(
                  form.toDict(),
                  {app.session_cookie_name : session.serialize()}
              ) 

            data = json.loads(response)

            flash("Account successfully created!", "success")

        return redirect(url_for('login'))


    @normal_permission.require(http_exception=403)
    def delete(self):
        raise NotYetImplemented()


app.add_url_rule('/<username>',
                    view_func=UserAPI.as_view('users'),
                    methods=['GET'])
app.add_url_rule('/users',\
                    view_func=UserAPI.as_view('users'),
                    methods=['PUT','POST'])
app.add_url_rule('/users/<username>',\
                    view_func=UserAPI.as_view('users'),
                    methods=['DELETE'])


@app.route('/api/users/new')
def userNewForm():
    form = RegistrationForm(request.form)
    return render_template('auth/register.html', form=form)
