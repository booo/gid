from web import app, db
from gid.gitrepository import GitRepository

association_table = db.Table('repository_user', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('repository_id', db.Integer, db.ForeignKey('repository.id'))
)

class Repository(db.Model):
    __tablename = 'repository'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(80))
    path          = db.Column(db.String(128))
    description   = db.Column(db.String(512))
    owner_id      = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner         = db.relationship('User')
    collaborators = db.relationship('User', secondary=association_table,\
                        backref=db.backref("repositories", lazy="dynamic"))

    def __init__(self, name, user):
        self.name = name
        self.owner = user
        GitRepository.create(name, user.username) 

    def __repr__(self):
        return '<Repository %r>' % self.name

    def __eq__(self, other):
      return self.name == other.name and self.owner == other.owner
