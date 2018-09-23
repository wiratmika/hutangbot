import hashlib
import time
from django.shortcuts import render
from django.http import JsonResponse
from .models import Debt


def create(request, is_add):
    try:
        payload = parse(request.POST['text'])
    except ValueError as err:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': 'Gagal menambahkan hutang',
            'attachments': [{
                'text': str(err)
            }]
        })

    sha1 = hashlib.sha1()
    sha1.update(str(time.time()).encode('utf-8'))

    debt = Debt.objects.create(
        transaction_id=sha1.hexdigest()[:5],
        source=request.POST['user_name'],
        source_slack_id=request.POST['user_id'],
        target=payload['user_name'],
        target_slack_id=payload['user_id'],
        amount=payload['amount']
    )

    return JsonResponse({
        'response_type': 'ephemeral',
        'text': 'Berhasil menambahkan hutang',
        'attachments': [{
            'text': 'Kamu berhutang sejumlah ' + beautify_amount(debt.amount) + ' ke ' + debt.target
        }]
    })


def parse(input):
    content = input.split(' ')
    if (len(content) is not 2):
        raise ValueError(
            'Jumlah parameter terlalu panjang atau terlalu pendek')

    user = content[0]

    return {
        'user_name': user[user.index('|') + 1:-1],
        'user_id': user[2:user.index('|')],
        'amount': content[1]
    }


def beautify_amount(amount):
    return 'Rp ' + '{:,}'.format(int(amount))
