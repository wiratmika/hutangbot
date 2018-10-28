from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from debts.models import Debt
from debts.serializers import CommandSerializer, DebtSerializer, TotalSerializer
from debts.utils import generate_ledger


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
    serializer = CommandSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    # TODO: optimize this to aggregate in DB instead
    # TODO: maybe can also use ViewSet
    own_debts = Debt.objects.filter(source_slack_id=user_id)
    other_debts = Debt.objects.filter(target_slack_id=user_id)

    result = TotalSerializer(
        data=generate_ledger(own_debts, other_debts),
        many=True
    )
    result.is_valid()

    return Response({
        'response_type': 'ephemeral',
        'attachments': [{
            'fields': [{
                'title': 'Berikut list hutang kamu',
                'value': '\n'.join(result.data)
            }],
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    })
