from web import app, db

from web.models.repository import Repository

class AssociationUserRepo(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'), primary_key=True)
    repository = db.relationship("Repository")
