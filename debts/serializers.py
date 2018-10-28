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
        content = data['text'].split(' ')
        if (len(content) is not 2):
            raise serializers.ValidationError(
                'Jumlah parameter terlalu panjang atau terlalu pendek')

        # TODO: validate user
        user = content[0]
        # TODO: check for any non-numeric char
        amount = int(content[1])

        if amount <= 0:
            raise serializers.ValidationError(
                'Jumlah hutang atau pembayaran tidak boleh negatif')

        source_slack_id = data.get('user_id')
        target = user[user.index('|') + 1:-1]
        target_slack_id = user[2:user.index('|')]

        if not self.context['is_add']:
            past_debt = Debt.objects.get_total_for(
                source_slack_id, target_slack_id)

            if amount > past_debt:
                raise serializers.ValidationError(
                    f'Kamu hanya berhutang sejumlah {past_debt} ke {target}')

        return {
            'transaction_id': generate_transaction_id(),
            'source': data['user_name'],
            'source_slack_id': source_slack_id,
            'target': target,
            'target_slack_id': target_slack_id,
            'amount': amount if self.context['is_add'] else -amount
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
                        'value': beautify_amount(Debt.objects.get_total_for(
                            obj.source_slack_id,
                            obj.target_slack_id
                        )),
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


class TotalSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj['amount'] == 0:
            return f"Kamu sudah impas dengan {obj['name']}. Selamat!"

        if obj['amount'] > 0:
            return f"Kamu masih berhutang ke {obj['name']} sebesar {beautify_amount(obj['amount'])}"
        else:
            return f"{obj['name']} masih berhutang ke kamu sebesar {beautify_amount(obj['amount'])}"
