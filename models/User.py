from .db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone
        }
