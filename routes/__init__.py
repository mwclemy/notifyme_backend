from .users_routes import apply_users_routes
from .plaid_routes import apply_plaid_routes

# this is a function that takes in an app object
# we import this function in application.py and invoke it, passing it our app object


def apply_routes(app):
    apply_users_routes(app)
    apply_plaid_routes(app)
