import hashlib
from django.shortcuts import render
from django.http import HttpResponse
from .models import Debt

def create(request):
    debt = Debt()
    debt.transaction_id = hashlib.sha256(b'mika').hexdigest()[:5]
    debt.source = request.POST['user_name']
    debt.source_slack_id = request.POST['user_id']
    debt.target = 'abdul'
    debt.target_slack_id = 'U123123123'
    debt.amount = 50000
    debt.save()
    return HttpResponse('SHIP!')
