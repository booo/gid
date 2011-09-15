from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from twisted.conch.ssh.keys import Key as SSHKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id        = db.Column(db.Integer,     primary_key=True)
    username  = db.Column(db.String(80),  unique=True)
    email     = db.Column(db.String(120), unique=True)
    password  = db.Column(db.String(128))
    key       = db.Column(db.String(512))
    keyBlob   = db.Column(db.Binary(512))

    repositories = db.relationship('AssociationUserRepo')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'
        self.keyBlob = SSHKey.fromString(data = self.key).blob()

    def __repr__(self):
        return '<User %r>' % self.username
