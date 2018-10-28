from django.db import models

from debts.utils import generate_ledger


class DebtManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)

    def get_total_for(self, source_slack_id, target_slack_id):
        own_debts = Debt.objects.filter(
            source_slack_id=source_slack_id,
            target_slack_id=target_slack_id
        )
        other_debts = Debt.objects.filter(
            source_slack_id=target_slack_id,
            target_slack_id=source_slack_id
        )
        return list(generate_ledger(own_debts, other_debts))[0]['amount']


class Debt(models.Model):
    objects = DebtManager()

    transaction_id = models.CharField(max_length=6, unique=True)
    source = models.CharField(max_length=100)
    source_slack_id = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    target_slack_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.source + ' owes ' + self.target + ' ' + str(self.amount)
