import jwt
import models
import os
from flask import Flask, request
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


def create_user():
    existing_user = models.User.query.filter_by(
        phone=request.json["phone"]).first()
    if existing_user:
        return {"message": "Phone must be present and unique"}, 400

    hashed_pw = bcrypt.generate_password_hash(
        request.json["password"]).decode('utf-8')
    user = models.User(
        name=request.json["name"],
        phone=request.json["phone"],
        password=hashed_pw,
    )

    models.db.session.add(user)
    models.db.session.commit()

    encrypted_id = jwt.encode({"user_id": user.id}, os.environ.get(
        'JWT_SECRET'), algorithm="HS256").decode('utf-8')
    return {"user": user.to_json(), "user_id": encrypted_id}


def login():
    user = models.User.query.filter_by(phone=request.json["phone"]).first()
    if not user:
        return {"message": "User not found"}, 404

    if bcrypt.check_password_hash(user.password, request.json["password"]):
        encrypted_id = jwt.encode({"user_id": user.id}, os.environ.get(
            'JWT_SECRET'), algorithm="HS256").decode('utf-8')
        print(encrypted_id)
        return {"user": user.to_json(), "user_id": encrypted_id}
    else:
        return {"message": "Password incorrect"}, 401


def verify_user():
    print(request.headers["Authorization"])
    print(os.environ.get(
        'JWT_SECRET'))
    decrypted_id = jwt.decode(request.headers["Authorization"], os.environ.get(
        'JWT_SECRET'), algorithms=["HS256"])["user_id"]
    user = models.User.query.filter_by(id=decrypted_id).first()
    if not user:
        return {"message": "user not found"}, 404
    return {"user": user.to_json()}
