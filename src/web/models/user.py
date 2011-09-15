from web import app, db
from web.models.associationUserRepo import AssociationUserRepo
from twisted.conch.ssh.keys import Key as SSHKey

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
        self.key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAzZCCriNjaN6wpB7T049mRQXZTHtnTQSUW3k5D+scqUOuijQeOEmDp99CEOqnAzCSon5aLTBYKtdQiLSDt4+YSKlnQsJ8JydZXWIX7wxyiPMqixZpigStQN5TO57mB6WonShWW7fcPfgVCABhmApASHJ8rSLYSm5iwx5Ke+A2lC8Nr5m9r9r8tkxyTgMn5Sp60ziZ+fsKI3/EW6SWmFIyISmyZB8KXp911Hv72QVYtcbCUP9ABxuW4CUMWB9SFog+UzvhtJeDo7Z+eKeXYkOQagDzO1SAHaa6eD8CPj85hXuHQvXsJAiSOILaj8zf8ej7WOkjlRL1Z0QFnzk/AKBCcQ== john@John-Does-MacBook-Pro.local'
        self.keyBlob = SSHKey.fromString(data = self.key).blob()

    def __repr__(self):
        return '<User %r>' % self.username
