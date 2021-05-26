import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import models
from routes import apply_routes

import jwt

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')

CORS(app)

bcrypt = Bcrypt(app)

models.db.init_app(app)


@app.before_request
def lookup_user():
    try:
        if request.headers["Authorization"]:
            decrypted_id = jwt.decode(request.headers["Authorization"], os.environ.get(
                'JWT_SECRET'), algorithms=["HS256"])["user_id"]
            user = models.User.query.filter_by(id=decrypted_id).first()
            request.user = user
        else:
            request.user = None
    except Exception as e:
        print(e)


def root():
    return {"message": "ok"}


app.route('/', methods=["GET"])(root)

apply_routes(app)

if __name__ == '__main__':
    port = os.environ.get('PORT') or 5000
    app.run(port=port, debug=True)
