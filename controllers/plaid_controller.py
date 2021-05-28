from plaid.model.amount import Amount
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.nullable_recipient_bacs import NullableRecipientBACS
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import PaymentInitiationRecipientCreateRequest
from plaid.model.payment_initiation_payment_create_request import PaymentInitiationPaymentCreateRequest
from plaid.model.payment_initiation_payment_get_request import PaymentInitiationPaymentGetRequest
from plaid.model.link_token_create_request_payment_initiation import LinkTokenCreateRequestPaymentInitiation
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.asset_report_create_request import AssetReportCreateRequest
from plaid.model.asset_report_create_request_options import AssetReportCreateRequestOptions
from plaid.model.asset_report_user import AssetReportUser
from plaid.model.asset_report_get_request import AssetReportGetRequest
from plaid.model.asset_report_pdf_get_request import AssetReportPDFGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.api import plaid_api
from flask import render_template
from flask import request as req
from flask import jsonify
from datetime import datetime
from datetime import timedelta
import plaid
import base64
import os
import datetime
import json
import time
import math
from twilio.rest import Client as TwilioClient

import models
from dotenv import load_dotenv
load_dotenv()

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

MAX_TRANSACTIONS_PER_PAGE = 500
OMIT_CATEGORIES = ["Transfer", "Credit Card", "Deposit", "Payment"]
OMIT_ACCOUNT_SUBTYPES = ['cd', 'savings']

twilio_client = TwilioClient(
    os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))


def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value


host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))


# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_id is only relevant for the UK Payment Initiation product.
# We store the payment_id in memory - in production, store it in a secure
# persistent data store.
payment_id = None

item_id = None


def info():
    global access_token
    global item_id
    return jsonify({
        'item_id': item_id,
        'access_token': access_token,
        'products': PLAID_PRODUCTS
    })


def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Notifyme",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )
        # create link token
        response = client.link_token_create(request)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)


def get_access_token():
    # global access_token
    # global item_id
    public_token = req.form['public_token']
    user = req.user
    if user:
        try:
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token)
            exchange_response = client.item_public_token_exchange(
                exchange_request)
            pretty_print_response(exchange_response.to_dict())
            # access_token = exchange_response['access_token']
            # item_id = exchange_response['item_id']
            # Save access token to the db
            access_token = models.AccessToken(
                access_token=exchange_response['access_token']
            )
            user.access_tokens.append(access_token)
            models.db.session.add(user)
            models.db.session.commit()
            return jsonify(exchange_response.to_dict())
        except plaid.ApiException as e:
            return json.loads(e.body)
    else:
        return {"message": "user not found"}, 404


def get_auth():
    try:
        request = AuthGetRequest(
            access_token=access_token
        )
        response = client.auth_get(request)
        pretty_print_response(response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)


def all_transactions(access_token, start_date, end_date):
    options = TransactionsGetRequestOptions()
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date.date(),
        end_date=end_date.date(),
        options=options
    )
    response = client.transactions_get(request)
    transactions = response.transactions
    return transactions


def get_yesterdays_transactions(access_token, start_date, end_date):

    account_ids = [account['account_id'] for account in client.accounts_get(
        AccountsGetRequest(access_token=access_token))['accounts']
        if account['subtype'] not in OMIT_ACCOUNT_SUBTYPES]

    num_available_transactions = client.transactions_get(TransactionsGetRequest(access_token, start_date, end_date,
                                                                                options=TransactionsGetRequestOptions(
                                                                                    account_ids=account_ids)
                                                                                ))['total_transactions']
    num_pages = math.ceil(num_available_transactions /
                          MAX_TRANSACTIONS_PER_PAGE)
    transactions = []

    for page_num in range(num_pages):
        transactions += [transaction
                         for transaction in client.transactions_get(TransactionsGetRequest(access_token, start_date, end_date,
                                                                                           options=TransactionsGetRequestOptions(
                                                                                               account_ids=account_ids, offset=page_num * MAX_TRANSACTIONS_PER_PAGE,
                                                                                               count=MAX_TRANSACTIONS_PER_PAGE)

                                                                                           ))['transactions']
                         if transaction['category'] is None
                         or not any(category in OMIT_CATEGORIES
                                    for category in transaction['category'])]

    return transactions


def get_institution(access_token):
    request = ItemGetRequest(access_token=access_token)
    response = client.item_get(request)
    request = InstitutionsGetByIdRequest(
        institution_id=response['item']['institution_id'],
        country_codes=[CountryCode('US')]
    )
    institution_response = client.institutions_get_by_id(request)
    return institution_response


def get_transactions():
    # Pull transactions for the last 30 days
    start_date = (datetime.datetime.now() - timedelta(days=30))
    end_date = datetime.datetime.now()
    user = req.user
    if user:
        try:
            access_tokens = user.access_tokens
            transactions = []
            for access_token in access_tokens:
                transactions += all_transactions(
                    access_token.access_token, start_date, end_date)
            return jsonify({"transactions":  [t.to_dict() for t in transactions]})
        except plaid.ApiException as e:
            error_response = format_error(e)
            return jsonify(error_response)

    else:
        return {"message": "user not found"}, 400


def get_institutions():
    user = req.user
    if user:
        try:
            access_tokens = user.access_tokens
            institutions = []
            for access_token in access_tokens:
                institutions.append(get_institution(
                    access_token.access_token))
            return jsonify({"institutions":  [i.to_dict()['institution'] for i in institutions]})
        except plaid.ApiException as e:
            error_response = format_error(e)
            return jsonify(error_response)

    else:
        return {"message": "user not found"}, 400


def send_notification():
    # Pull Yesterday's transactions
    # start_date = (datetime.date.today() -
    #               datetime.timedelta(days=1))
    # end_date = (datetime.date.today() -
    #             datetime.timedelta(days=1))

    # Pull transactions for the last 30 days
    start_date = (datetime.date.today() - timedelta(days=30))
    end_date = datetime.date.today()
    user = req.user
    if user:
        try:
            access_tokens = user.access_tokens
            transactions = []
            for access_token in access_tokens:
                transactions += get_yesterdays_transactions(
                    access_token.access_token, start_date, end_date)
            total_spent = sum(transaction['amount']
                              for transaction in transactions)
            if (total_spent > user.threshold_amount):
                message = f'You spent ${total_spent} yesterday. 💸'
                twilio_client.messages.create(
                    to=user.phone, from_=os.getenv('MY_TWILIO_NUM'), body=message)
            return jsonify({"transactions":  [t.to_dict() for t in transactions], "total_spent": total_spent})
        except plaid.ApiException as e:
            error_response = format_error(e)
            return jsonify(error_response)

    else:
        return {"message": "user not found"}, 400


def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True))


def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}
