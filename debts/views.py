from rest_framework.decorators import api_view
from rest_framework.response import Response

from debts.models import Debt
from debts.serializers import DebtSerializer


@api_view(['POST'])
def list(request):
    return Response()


@api_view(['POST'])
def create_debt(request):
    serializer = DebtSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
def create_payment(request):
    return Response()


@api_view(['POST'])
def create_receivable(request):
    return Response(serializer.data)


@api_view(['POST'])
def delete(request):
    return Response(serializer.data)


@api_view(['POST'])
def calculate(request):
    return Response(serializer.data)
