from flaskext.login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user
# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

#from flask import Flask
#from flaskext.sqlalchemy import SQLAlchemy
#
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#db = SQLAlchemy(app)
#
#
#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(80), unique=True)
#    email = db.Column(db.String(120), unique=True)
#
#    def __init__(self, username, email):
#        self.username = username
#        self.email = email
#
#    def __repr__(self):
#        return '<User %r>' % self.username
