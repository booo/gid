
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from web import app
from web.models.rest import RestResource, ResourceNotFound
from web.views.auth.session import normal_permission

from api.forms.profile import ProfileForm
from api.forms.registration import RegistrationForm
from api.models.dictobject import DictObject

class UserAPI(MethodView):

    rest = RestResource('http://' + app.config['SERVER_NAME_API'] + '/api/users')

    def get(self, username):
        url = '/%s' % username
        try: 
          response = UserAPI.rest.get(
                url,
                headers = {'Accept': 'application/json'}
              ).body_string()

          user = json.loads(response)['user']
          amountOfRepositories= len(
              filter(
                lambda x: x['owner']['username'] == user['username'],
                user['repos']
              )
            )


          return render_template('auth/user.html',
                        user=user, amountOfRepositories=amountOfRepositories
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
                  username = session['user.username'],
                  password = session['user.password']
              ) 

            data = json.loads(response)

            flash("Successfully updated your profile!", "success")


        return render_template('auth/profile.html', form=form)


    def post(self):
        form = RegistrationForm(request.form)

        if form.validate():

            response = self.rest.postForm(
                  form.toDict()
              ) 

            data = json.loads(response)

            flash("Account successfully created!", "success")

        return redirect(url_for('login'))


    def delete(self):
        raise NotYetImplemented()


app.add_url_rule('/<username>',
                    view_func=UserAPI.as_view('users'),
                    methods=['GET'])
app.add_url_rule('/users',
                    view_func=UserAPI.as_view('users'),
                    methods=['PUT','POST'])
app.add_url_rule('/users/<username>',
                    view_func=UserAPI.as_view('users'),
                    methods=['DELETE'])


@app.route('/api/users/new')
def userNewForm():
    form = RegistrationForm(request.form)
    return render_template('auth/register.html', form=form)
