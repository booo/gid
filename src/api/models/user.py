from api import app, db
from api.models.repository import Repository
from api.models.activity import Activity
from twisted.conch.ssh.keys import Key as SSHKey
from random import choice

from sqlalchemy.ext.hybrid import hybrid_property


class _KeyBlobUpdater(db.MapperExtension):
    def before_create(self, mapper, connection, instance):
        if instance.key:
          instance.keyBlob = SSHKey.fromString(data = instance.key).blob()

        instance.token = ''.join(
           choice(
              string.ascii_uppercase + string.digits
           ) for x in range(N)
        )


    def before_update(self, mapper, connection, instance):
        if instance.key:
          instance.keyBlob = SSHKey.fromString(data = instance.key).blob()

class User(db.Model):
    __tablename = 'user'

    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True)
    email         = db.Column(db.String(120), unique=True)
    passwordHash  = db.Column(db.String(128))
    key           = db.Column(db.String(512))
    token         = db.Column(db.String(12128))
    keyBlob       = db.Column(db.Binary(512))
    activities    = db.relationship("Activity")

    __mapper_args__ = {'extension': _KeyBlobUpdater()}


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


    @hybrid_property
    def password(self):
        return self.passwordHash


    @password.setter
    def password(self, value):
        import hashlib
        self.passwordHash = hashlib.sha1(value).hexdigest()


    def toDict(self, short = True, filterPublic = False):
        user = {
            'username' : self.username,
            'email'    : self.email
          }

        if not short:
          if filterPublic:
            repos = filter(lambda x: x.private == False, self.repos)
          else:
            repos = self.repos

          user['repos'] = [r.toDict() for r in repos]
          user['activities'] = [a.toDict() for a in self.activities]

        return user
