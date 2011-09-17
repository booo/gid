
from flask import Flask, request, render_template, json, \
                                flash, session, redirect, url_for, Response, \
                                jsonify

from flask.views import MethodView



from web import app
from web.models.user import User, db
from web.views.auth.session import normal_permission
from web.forms.registration import RegistrationForm
from web.forms.login import LoginForm
from web.forms.profile import ProfileForm


class UserAPI(MethodView):

    def get(self, username=None):
        if username == None:
            users = []
            for user in User.query.all():
                data = {
                  'name' : user.username,
                  'email' : user.email
                }
                users.append(data)
            
            if "application/json" in request.headers['Accept']:
                return jsonify(users = users)
            else:
                return render_template('auth/users.html', users=users)


        else:
            user = User.query.filter_by(username = username).first()

            repoOwn = []
            repoCollaborating = []
            for repo in user.repositories:
                if repo.owner == user:
                  repoOwn.append(repo.name)
                else:
                  repoCollaborating.append({
                      'name' : repo.name,
                      'owner': repo.owner.username
                    }
                  )

            obj = {
              'name' : user.username,
              'email' : user.email,
              'repositories': {
                'own': repoOwn,
                'collaborating': repoCollaborating
              }
            }
            
            if "application/json" in request.headers['Accept']:
              return jsonify(user=obj)
            else:
              return render_template('auth/user.html', user=obj)


    @normal_permission.require(http_exception=403)
    def put(self):
        form = ProfileForm(request.form)
        if form.validate():
            user = User.query.filter_by(username = session['identity.name']).first()
            user.username = form.username.data 
            user.email = form.email.data 
            user.key = form.key.data 
            
            db.session.add(user)
            db.session.commit()

            flash("Updated profile informations", "success")
            
            return redirect(url_for('session'))

        return render_template('auth/profile.html', form=form)


    def post(self):
        form = RegistrationForm(request.form)
        
        if form.validate():

            if not User.query.filter_by(username = form.username.data).count() > 0:
                user = User(form.username.data, form.email.data,
                            form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Thanks for registering',"success")
                return redirect(url_for('users'))

            else:
                flash("Username already exist", "error")

        return render_template('auth/register.html', form=form)


    @normal_permission.require(http_exception=403)
    def delete(self):
        raise NotYetImplemented()

app.add_url_rule('/users/',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET','PUT','POST'])
app.add_url_rule('/users/<username>',\
                    view_func=UserAPI.as_view('users'),
                    methods=['GET', 'DELETE'])


@app.route('/users/new')
def userNewForm():
    form = RegistrationForm(request.form)
    return render_template('auth/register.html', form=form)
