from .db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String, nullable=False, unique=True)
    threshold_amount = db.Column(db.Numeric(
        10, 2, asdecimal=False, decimal_return_scale=None))
    password = db.Column(db.String)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "threshold_amount": self.threshold_amount
        }
