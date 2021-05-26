from .db import db


class AccessToken(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='access_tokens')

    def to_json(self):
        return {
            "id": self.id,
            "access_token": self.access_token
        }
