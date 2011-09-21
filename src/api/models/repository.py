import os
import shutil
from datetime import datetime

from api import app, db

from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app


from git.repository import GitRepository

association_table = db.Table('repository_user', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('repository_id', db.Integer, db.ForeignKey('repository.id'))
)

class Repository(db.Model):
    __tablename = 'repository'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(80))
    createdAt     = db.Column(db.DateTime(), default=datetime.now)
    private       = db.Column(db.Boolean(), default=True)
    path          = db.Column(db.String(128))
    description   = db.Column(db.String(512))

    owner_id      = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner         = db.relationship('User')

    contributers  = db.relationship('User', secondary=association_table,\
                        backref=db.backref("repos", lazy="dynamic"))

    @hybrid_property
    def cloneUrl(self):
        return 'ssh://$USER@%s/%s/%s' % (\
                    str(current_app.config['SERVER_NAME_GIT']),
                    self.owner.username,
                    self.name
                  )


    @hybrid_property
    def git(self):
        if not hasattr(self, '_git'):
            self._git = GitRepository(self.path)

        return self._git


    def __init__(self, reponame, owner):
        self.name  = reponame
        self.owner = owner
        self.path  = os.path.join(
                        app.config['GIT_DATA_DIR'],
                        owner.username,
                        reponame
                     )
        self._git = GitRepository(self.path, True)


    def __repr__(self):
        return '<Repository %r>' % self.name


    def __eq__(self, other):
        return self.name == other.name and self.owner == other.owner

    def toDict(self):
        return {
            'name'          : self.name,
            'createdAt'     : self.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
            'private'       : self.private,
            'path'          : self.path,
            'cloneUrl'      : self.cloneUrl,
            'description'   : self.description,
            'owner'         : self.owner.toDict(True),
            'contributers'  : [c.toDict(True) for c in self.contributers],
            'git'           : self.git.toDict()
          }
