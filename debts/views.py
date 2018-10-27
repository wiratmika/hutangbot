from django.shortcuts import render
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from debts.models import Debt
from debts.serializers import DebtSerializer
from debts.utils import beautify_amount


class DebtList(APIView):
    @transaction.atomic
    def post(self, request, is_add):
        serializer = DebtSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'response_type': 'ephemeral',
                'attachments': [{
                    'text': 'Gagal menambahkan hutang',
                    'fields': [
                        {
                            'text': 'Penyebab',
                            'value': serializer.errors,
                        }
                    ],
                    'color': 'bad'
                }]
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        transaction_id = serializer.validated_data['transaction_id']
        target = serializer.validated_data['target']
        amount = serializer.validated_data['amount']

        # TODO: Make it a function
        instruction = (
            f"Untuk membatalkan, kirim `/hapus {transaction_id}`\n"
            f"Untuk membayar, ketik `/bayar @{target} {amount}` atau `/bayar {transaction_id}`\n"
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
                        'value': beautify_amount(amount),
                        'short': True
                    },
                    {
                        'title': 'Ke',
                        'value': target,
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
