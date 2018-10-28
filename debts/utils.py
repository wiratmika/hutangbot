import hashlib
import time

from django.utils import timezone
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response


def slack_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Not DRF validation error
    if not isinstance(response, Response):
        return response

    response.status_code = status.HTTP_200_OK
    response.data = {
        'response_type': 'ephemeral',
        'attachments': [{
            'text': 'Gagal menambahkan hutang atau pembayaran :cry:',
            'fields': [
                {
                    'title': 'Penyebab',
                    'value': response.data[0],
                }
            ],
            'color': 'danger',
            'ts': timezone.now().timestamp()
        }]
    }

    return response


def beautify_amount(amount):
    return 'Rp ' + '{:,}'.format(int(amount))


# TODO: handle when empty
def generate_ledger(own_debts, other_debts):
    ledger = {}

    for debt in own_debts:
        info = ledger.get(debt.target_slack_id, {
            'name': debt.target,
            'amount': 0
        })
        info['amount'] += debt.amount
        ledger[debt.target_slack_id] = info

    for debt in other_debts:
        info = ledger.get(debt.target_slack_id, {
            'name': debt.target,
            'amount': 0
        })
        info['amount'] -= debt.amount
        ledger[debt.target_slack_id] = info

    return ledger.values()


def generate_transaction_id():
    sha1 = hashlib.sha1()
    sha1.update(str(time.time()).encode('utf-8'))
    return sha1.hexdigest()[:5]


# TODO: implement validation if user is malformed
def parse_user(user):
    return {
        'name': user[user.index('|') + 1:-1],
        'slack_id': user[2:user.index('|')]
    }
