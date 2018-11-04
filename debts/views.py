from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from debts.models import Debt
from debts.serializers import CommandSerializer, DebtSerializer, ListSerializer, TotalSerializer
from debts.utils import generate_ledger


@api_view(['POST'])
def list(request):
    serializer = CommandSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    debts = Debt.objects.filter(
        Q(source_slack_id=user_id) | Q(target_slack_id=user_id))
    result = ListSerializer(
        data=debts,
        many=True,
        context={'user_id': user_id}
    )
    result.is_valid()

    if len(result.data) == 0:
        return Response({
            'response_type': 'ephemeral',
            'attachments': [{
                'text': 'Kamu belum memiliki transaksi. Pakai botnya, dong!',
                'color': 'good',
                'ts': timezone.now().timestamp()
            }]
        })

    return Response({
        'response_type': 'ephemeral',
        'attachments': [{
            'fields': [{
                'title': 'Berikut daftar transaksi kamu',
                'value': '\n'.join(result.data)
            }],
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    })


@api_view(['POST'])
def create_debt(request):
    serializer = DebtSerializer(data=request.data, context={'is_add': True})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
def create_payment(request):
    serializer = DebtSerializer(data=request.data, context={'is_add': False})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
def create_receivable(request):
    return Response(serializer.data)


@api_view(['POST'])
# TODO: handle if deleted then payment > debts!?
def delete(request):
    serializer = CommandSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']
    # TODO: Validate for hashtag
    transaction_id = serializer.validated_data['text'][1:]

    try:
        debt = Debt.objects.get(source_slack_id=user_id,
                                transaction_id=transaction_id)
    except Debt.DoesNotExist:
        raise serializers.ValidationError(
            'Transaksi tidak ditemukan atau bukan dibuat oleh kamu')

    debt.deleted_at = timezone.now()
    debt.save()

    return Response({
        'response_type': 'ephemeral',
        'attachments': [{
            'text': 'Berhasil menghapus transaksi :tada:',
            'fields': [
                {
                    'title': 'ID Transaksi',
                    'value': serializer.validated_data['text'],
                    'short': True
                },
                {
                    'title': 'Jumlah/Sisa Hutang',
                    'value': 'To be implemented',
                    'short': True
                }
            ],
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    })


@api_view(['POST'])
# TODO: might as well merge with list function, just different command
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

    if len(result.data) == 0:
        return Response({
            'response_type': 'ephemeral',
            'attachments': [{
                'text': 'Kamu tidak memiliki hutang piutang. Selamat menikmati hidup!',
                'color': 'good',
                'ts': timezone.now().timestamp()
            }]
        })

    return Response({
        'response_type': 'ephemeral',
        'attachments': [{
            'fields': [{
                'title': 'Berikut daftar hutang kamu',
                'value': '\n'.join(result.data)
            }],
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    })
