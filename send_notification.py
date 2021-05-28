import os

from twilio.rest import Client as TwilioClient

from get_yesterdays import get_yesterdays_transactions

twilio_client = TwilioClient(
    os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))


def send_summary(transactions):
    total_spent = sum(transaction['amount'] for transaction in transactions)
    message = f'You spent ${total_spent} yesterday. 💸'
    twilio_client.api.account.messages.create(to=os.getenv(
        'MY_CELL'), from_=os.getenv('MY_TWILIO_NUM'), body=message)


if __name__ == "__main__":
    send_summary(get_yesterdays_transactions())
