import hashlib
import time

from rest_framework import status
from rest_framework.views import exception_handler


def slack_exception_handler(exc, context):
    response = exception_handler(exc, context)
    response.status_code = status.HTTP_200_OK
    response.data = {
        'response_type': 'ephemeral',
        'attachments': [{
            'text': 'Gagal menambahkan hutang',
            'fields': [
                {
                    'title': 'Penyebab',
                    'value': response.data[0],
                }
            ],
            'color': 'danger'
        }]
    }

    return response


def beautify_amount(amount):
    return 'Rp ' + '{:,}'.format(int(amount))


def generate_transaction_id():
    sha1 = hashlib.sha1()
    sha1.update(str(time.time()).encode('utf-8'))
    return sha1.hexdigest()[:5]
