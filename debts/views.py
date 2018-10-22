import hashlib
import time
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from debts.models import Debt
from debts.utils import beautify_amount


class DebtList(APIView):
    def post(self, request, is_add):
        try:
            payload = self.parse(request.data['text'])
        except ValueError as err:
            return Response({
                'response_type': 'ephemeral',
                'text': 'Gagal menambahkan hutang',
                'attachments': [{
                    'text': str(err)
                }]
            }, status=status.HTTP_400_BAD_REQUEST)

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

        return Response({
            'response_type': 'ephemeral',
            'text': 'Berhasil menambahkan hutang',
            'attachments': [{
                'text': 'Kamu berhutang sejumlah ' + beautify_amount(debt.amount) + ' ke ' + debt.target
            }]
        }, status=status.HTTP_201_CREATED)

    def parse(self, input):
        content = input.split(' ')
        if (len(content) is not 2):
            raise ValueError(
                'Jumlah parameter terlalu panjang atau terlalu pendek')

        user = content[0]
        amount = int(content[1])

        if (amount <= 0):
            raise ValueError('Jumlah hutang tidak boleh negatif')

        return {
            'user_name': user[user.index('|') + 1:-1],
            'user_id': user[2:user.index('|')],
            'amount': amount
        }
