

from rest_framework import serializers

from debts.models import Debt
from debts.utils import generate_transaction_id


class DebtSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        content = data.get('text').split(' ')
        if (len(content) is not 2):
            raise serializers.ValidationError({
                'text': 'Jumlah parameter terlalu panjang atau terlalu pendek'
            })

        # TODO: validate user
        user = content[0]
        # TODO: strip of all punctuations?
        amount = int(content[1])

        if (amount <= 0):
            raise serializers.ValidationError({
                'text': 'Jumlah hutang tidak boleh negatif'
            })

        return {
            'transaction_id': generate_transaction_id(),
            'source': data.get('user_name'),
            'source_slack_id': data.get('user_id'),
            'target': user[user.index('|') + 1:-1],
            'target_slack_id': user[2:user.index('|')],
            'amount': amount
        }

    def create(self, validated_data):
        return Debt.objects.create(**validated_data)
