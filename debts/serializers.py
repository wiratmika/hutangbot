from django.utils import timezone
from rest_framework import serializers

from debts.models import Debt
from debts.utils import beautify_amount, generate_transaction_id


class CommandSerializer(serializers.Serializer):
    command = serializers.CharField()
    user_id = serializers.CharField()
    user_name = serializers.CharField()


class DebtSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        content = data.get('text').split(' ')
        if (len(content) is not 2):
            raise serializers.ValidationError(
                'Jumlah parameter terlalu panjang atau terlalu pendek')

        # TODO: validate user
        user = content[0]
        # TODO: check for any non-numeric char
        amount = int(content[1])

        if (amount <= 0):
            raise serializers.ValidationError(
                'Jumlah hutang tidak boleh negatif')

        return {
            'transaction_id': generate_transaction_id(),
            'source': data.get('user_name'),
            'source_slack_id': data.get('user_id'),
            'target': user[user.index('|') + 1:-1],
            'target_slack_id': user[2:user.index('|')],
            'amount': amount
        }

    def to_representation(self, obj):
        instruction = (
            f'Untuk membatalkan, kirim `/hapus {obj.transaction_id}`\n'
            f'Untuk membayar, ketik `/bayar @{obj.target} {obj.amount}` atau `/bayar {obj.transaction_id}`\n'
            'Untuk melihat semua hutang/piutang yang kamu punya, kirim `/listhutang`\n'
            'Untuk melihat semua daftar transaksi, kirim `/listtransaksi`'
        )

        return {
            'response_type': 'ephemeral',
            'attachments': [{
                'text': 'Berhasil menambahkan hutang!',
                'fields': [
                    {
                        'title': 'ID Transaksi',
                        'value': obj.transaction_id,
                        'short': True
                    },
                    {
                        'title': 'Nilai',
                        'value': beautify_amount(obj.amount),
                        'short': True
                    },
                    {
                        'title': 'Ke',
                        'value': obj.target,
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
                'color': 'good',
                'ts': timezone.now().timestamp()
            }]
        }

    def create(self, validated_data):
        return Debt.objects.create(**validated_data)
