from api import app, db
from datetime import datetime

from api.models.repository import Repository

class Activity(db.Model):
    __tablename = 'activity'
    id            = db.Column(db.Integer, primary_key=True)
    activityType  = db.Column(db.String(80))
    date          = db.Column(db.DateTime(), default=datetime.now)

    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'))

    repo_id       = db.Column(db.Integer, db.ForeignKey('repository.id'))
    repo          = db.relationship('Repository')


    def __init__(self, activityType, repo):
        self.activityType = activityType
        self.repo = repo

    def toDict(self):
        return {
          'type' : self.activityType,
          'date' : self.date.strftime('%Y-%m-%d %H:%M:%S'),
          'repo' : self.repo.name
        }
