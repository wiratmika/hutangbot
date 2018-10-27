from django.db import transaction

from rest_framework.response import Response
from rest_framework.views import APIView

from debts.models import Debt
from debts.serializers import DebtSerializer


class DebtList(APIView):
    @transaction.atomic
    def post(self, request, is_add):
        serializer = DebtSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
