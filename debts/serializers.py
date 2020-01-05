from django.utils import timezone
from rest_framework import serializers

from debts.models import Debt
from debts.utils import beautify_amount, generate_transaction_id, parse_user


class CommandSerializer(serializers.Serializer):
    command = serializers.CharField()
    text = serializers.CharField(allow_blank=True)
    user_id = serializers.CharField()
    user_name = serializers.CharField()


class DebtSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        content = data['text'].split(' ')
        if (len(content) is not 2):
            raise serializers.ValidationError(
                'Jumlah parameter terlalu panjang atau terlalu pendek')

        target = parse_user(content[0])
        # TODO: check for any non-numeric char
        amount = int(content[1])

        if amount <= 0:
            raise serializers.ValidationError(
                'Jumlah hutang atau pembayaran tidak boleh nol atau negatif')

        source_slack_id = data.get('user_id')

        if not self.context['is_add']:
            past_debt = Debt.objects.get_total_for(
                source_slack_id, target['slack_id'])

            if past_debt == 0:
                raise serializers.ValidationError(
                    f'Kamu tidak memiliki hutang ke {target["name"]}')

            if amount > past_debt:
                raise serializers.ValidationError(
                    f'Kamu hanya berhutang sejumlah {beautify_amount(past_debt)} ke {target["name"]}')

        return {
            'transaction_id': generate_transaction_id(),
            'source': data['user_name'],
            'source_slack_id': source_slack_id,
            'target': target['name'],
            'target_slack_id': target['slack_id'],
            'amount': amount if self.context['is_add'] else -amount
        }

    def to_representation(self, obj):
        is_add = self.context['is_add']
        # TODO delete pay instruction when is_add=False
        instruction = (
            f'Untuk membatalkan, kirim `/hapus {obj.transaction_id}`\n'
            f'Untuk membayar, ketik `/bayar @{obj.target} {obj.amount}`\n'
            'Untuk melihat semua hutang/piutang yang kamu punya, kirim `/hutangku`\n'
            'Untuk melihat semua daftar transaksi, kirim `/transaksiku`'
        )

        text = 'Berhasil menambahkan hutang :tada:' if is_add else 'Berhasil melakukan pembayaran! :tada:'
        outstanding = Debt.objects.get_total_for(
            obj.source_slack_id,
            obj.target_slack_id
        )

        if not is_add and outstanding == 0:
            remarks = f'Selamat, kamu telah melunasi seluruh hutangmu ke {obj.target}!'
        else:
            remarks = beautify_amount(outstanding)

        return {
            'response_type': 'ephemeral',
            'attachments': [{
                'text': text,
                'fields': [
                    {
                        'title': 'ID Transaksi',
                        'value': f'#{obj.transaction_id}',
                        'short': True
                    },
                    {
                        'title': 'Nilai',
                        'value': beautify_amount(obj.amount if is_add else -obj.amount),
                        'short': True
                    },
                    {
                        'title': 'Ke',
                        'value': obj.target,
                        'short': True
                    },
                    {
                        'title': 'Jumlah Hutang' if is_add else 'Sisa Hutang',
                        'value': remarks,
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
            return f'Kamu sudah impas dengan {obj["name"]}. Selamat!'

        if obj['amount'] > 0:
            return f'Kamu masih berhutang ke {obj["name"]} sebesar {beautify_amount(obj["amount"])}'

        return f'{obj["name"]} masih berhutang ke kamu sebesar {beautify_amount(abs(obj["amount"]))}'


# TODO: is it possible to use serializers.ListSerializer?
class ListSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        action = 'berhutang' if obj.amount > 0 else 'membayar'
        amount = abs(obj.amount)
        prefix = f'[`#{obj.transaction_id}` {obj.created_at.strftime("%Y-%m-%d %H:%M:%S")}]'

        if obj.source_slack_id == self.context['user_id']:
            return f'{prefix} Kamu {action} ke {obj.target} sejumlah {beautify_amount(amount)}'

        return f'{prefix} {obj.target} {action} ke kamu sejumlah {beautify_amount(amount)}'
