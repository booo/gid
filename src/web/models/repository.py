from web import app, db
from gid.gitrepository import GitRepository

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    path = db.Column(db.String(128))
    description = db.Column(db.String(512))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, user):
        self.name = name
        self.owner = user
        GitRepository.create(name, user.username) 

    def __repr__(self):
        return '<Repository %r>' % self.name

    def __eq__(self, other):
      return self.name == other.name and self.owner == other.owner
