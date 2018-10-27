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
                'attachments': [{
                    'text': 'Gagal menambahkan hutang',
                    'fields': [
                        {
                            'text': 'Penyebab',
                            'value': str(err),
                        }
                    ],
                    'color': 'bad'
                }]
            }, status=status.HTTP_400_BAD_REQUEST)

        sha1 = hashlib.sha1()
        sha1.update(str(time.time()).encode('utf-8'))
        transaction_id = sha1.hexdigest()[:5]
        user_name = payload['user_name']
        amount = payload['amount']

        debt = Debt.objects.create(
            transaction_id=transaction_id,
            source=request.POST['user_name'],
            source_slack_id=request.POST['user_id'],
            target=user_name,
            target_slack_id=payload['user_id'],
            amount=amount
        )

        # TODO: Make it a function
        instruction = (
            f"Untuk membatalkan, kirim `/hapus {transaction_id}`\n"
            f"Untuk membayar, ketik `/bayar @{user_name} {amount}` atau `/bayar {transaction_id}`\n"
            "Untuk melihat semua hutang/piutang yang kamu punya, kirim `/listhutang`\n"
            "Untuk melihat semua daftar transaksi, kirim `/listtransaksi`"
        )

        return Response({
            'response_type': 'ephemeral',
            'attachments': [{
                'text': 'Berhasil menambahkan hutang!',
                'fields': [
                    {
                        'title': 'ID Transaksi',
                        'value': transaction_id,
                        'short': True
                    },
                    {
                        'title': 'Nilai',
                        'value': beautify_amount(debt.amount),
                        'short': True
                    },
                    {
                        'title': 'Ke',
                        'value': debt.target,
                        'short': True
                    },
                    {
                        'title': 'Jumlah Hutang',
                        'value': 'Please implement',
                        'short': True
                    },
                    {
                        'title': 'Keterangan',
                        'value': instruction
                    }
                ],
                'color': 'good'
            }]
        }, status=status.HTTP_201_CREATED)

    def parse(self, input):
        content = input.split(' ')
        if (len(content) is not 2):
            raise ValueError(
                'Jumlah parameter terlalu panjang atau terlalu pendek')

        # TODO: validate user
        user = content[0]
        amount = int(content[1])

        if (amount <= 0):
            raise ValueError('Jumlah hutang tidak boleh negatif')

        return {
            'user_name': user[user.index('|') + 1:-1],
            'user_id': user[2:user.index('|')],
            'amount': amount
        }
