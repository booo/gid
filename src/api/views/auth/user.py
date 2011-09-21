
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView

from restkit import ResourceNotFound

from sqlalchemy.exc import IntegrityError
from api import app
from api.models.user import User, db
from api.views.auth.session import requires_auth
from api.forms.registration import RegistrationForm
from api.forms.login import LoginForm
from api.forms.profile import ProfileForm


class UserAPI(MethodView):

    def get(self, username=None):
        if username == None:
            return jsonify(users=[ u.toDict() for u in User.query.all() ])

        else:
            user = User.query.filter_by(username = username).first()

            if user !=  None:
              return jsonify(user=user.toDict(False, True))

            return Response(""), 404


    @requires_auth
    def put(self):
        form = ProfileForm(request.form, csrf_enabled = False)

        if form.validate():
            user          = User.query.filter_by(
                              username = session['identity.name']
                            ).first()
            user.username = form.username.data 
            user.email    = form.email.data 
            user.key      = form.key.data 
            
            db.session.add(user)
            db.session.commit()

            return jsonify(user=user.toDict())

        return jsonify({'error': form.errors})


    def post(self):
        form = RegistrationForm(request.form, csrf_enabled = False)
        
        if form.validate():
            if not User.query.filter_by(username = form.username.data).count() > 0:
                try: 
                    user = User(form.username.data, form.email.data,
                                form.password.data)
                    db.session.add(user)
                    db.session.commit()

                    return jsonify(user=user.toDict())

                except IntegrityError as e:
                    return jsonify({"error": "Username or email do already exist"})


        return jsonify({"error": form.errors})


    @requires_auth
    def delete(self):
        raise NotYetImplemented()


app.add_url_rule('/api/users',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET','PUT','POST'])
app.add_url_rule('/api/users/<username>',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET', 'DELETE'])


@app.route('/api/users/new')
def userNewForm():
    form = RegistrationForm(request.form)
    return jsonify(form = form.toDict())
