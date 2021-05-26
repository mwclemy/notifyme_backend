from controllers import plaid_controller


def apply_plaid_routes(app):
    app.route('/api/info', methods=["POST"])(plaid_controller.info)
    app.route('/api/create_link_token',
              methods=["POST"])(plaid_controller.create_link_token)
    app.route('/api/set_access_token',
              methods=["POST"])(plaid_controller.get_access_token)
    app.route('/api/auth',
              methods=["GET"])(plaid_controller.get_auth)

    app.route('/api/transactions',
              methods=["GET"])(plaid_controller.get_transactions)

    app.route('/api/item',
              methods=["GET"])(plaid_controller.item)
