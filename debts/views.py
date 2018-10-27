from django.shortcuts import render
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from debts.models import Debt
from debts.serializers import DebtSerializer


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
                            'value': serializer.errors[0],
                        }
                    ],
                    'color': 'bad'
                }]
            }, status=status.HTTP_200_OK)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
