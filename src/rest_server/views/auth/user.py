
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView



from rest_server import app
from rest_server.models.user import User, db
from rest_server.views.auth.session import normal_permission
from rest_server.forms.registration import RegistrationForm
from rest_server.forms.login import LoginForm
from rest_server.forms.profile import ProfileForm


class UserAPI(MethodView):

    def get(self, username=None):
        if username == None:
            return jsonify(users=[ u.toDict() for u in User.query.all() ])

        else:
            user = User.query.filter_by(username = username).first()
            return jsonify(user=user.toDict(False))


    @normal_permission.require(http_exception=403)
    def put(self):
        form = ProfileForm(request.form)

        if form.validate():
            user          = User.query.filter_by(username = session['identity.name']).first()
            user.username = form.username.data 
            user.email    = form.email.data 
            user.key      = form.key.data 
            
            db.session.add(user)
            db.session.commit()

            return jsonify(user=user.toDict())

        return jsonifiy({ 'status':'invalid data'})


    def post(self):
        form = RegistrationForm(request.form)
        
        if form.validate():
            if not User.query.filter_by(username = form.username.data).count() > 0:
                user = User(form.username.data, form.email.data,
                            form.password.data)
                db.session.add(user)
                db.session.commit()

                return jsonify(user=user.toDict())

        return jsonifiy({ 'status':'invalid data'})


    @normal_permission.require(http_exception=403)
    def delete(self):
        raise NotYetImplemented()


app.add_url_rule('/api/users/',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET','PUT','POST'])
app.add_url_rule('/api/users/<username>',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET', 'DELETE'])


@app.route('/api/users/new')
def userNewForm():
    form = RegistrationForm(request.form)
    return jsonify(form = form.toDict())