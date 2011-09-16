from web import app, db
from web.models.repository import Repository
from twisted.conch.ssh.keys import Key as SSHKey


class _KeyBlobUpdater(db.MapperExtension):
    def before_create(self, mapper, connection, instance):
        if instance.key:
          instance.keyBlob = SSHKey.fromString(data = instance.key).blob()

    def before_update(self, mapper, connection, instance):
        if instance.key:
          instance.keyBlob = SSHKey.fromString(data = instance.key).blob()

class User(db.Model):
    __tablename = 'user'

    id        = db.Column(db.Integer,     primary_key=True)
    username  = db.Column(db.String(80),  unique=True)
    email     = db.Column(db.String(120), unique=True)
    password  = db.Column(db.String(128))
    key       = db.Column(db.String(512))
    keyBlob   = db.Column(db.Binary(512))

    __mapper_args__ = {'extension': _KeyBlobUpdater()}


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
