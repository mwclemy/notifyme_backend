from controllers import users_controller


def apply_users_routes(app):
    app.route('/users', methods=["POST"])(users_controller.create_user)
    app.route('/users/login', methods=["POST"])(users_controller.login)
    app.route('/users/verify', methods=["GET"])(users_controller.verify_user)
