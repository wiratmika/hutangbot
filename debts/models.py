from django.db import models

class Debt(models.Model):
    transaction_id = models.CharField(max_length=5)
    source = models.CharField(max_length=100)
    source_slack_id = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    target_slack_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.source + ' owes ' + self.target + ' ' + str(self.amount)