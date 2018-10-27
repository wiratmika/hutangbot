from rest_framework.decorators import api_view
from rest_framework.response import Response

from debts.models import Debt
from debts.serializers import DebtSerializer


@api_view(['POST'])
def add_debt(request):
    serializer = DebtSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
