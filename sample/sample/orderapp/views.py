# -*- coding: utf-8 -*-
from django.shortcuts import render
from decimal import Decimal
from rbkmoney import forms

def payment(request):
    form = forms.RequestRBKMoneyForm(initial={
        'orderId': 7,
        'serviceName': u'Два колеса, руль, педали и мешок свободы.',
        'recipientAmount': Decimal('10.00'),
        'recipientCurrency': u'RUR',
        'user_email': u'client@email.com',
        'userFields': ['some', 'values', 'list',],
    })

    template = 'orderapp/payment.html'
    context = {'form': form,}
    return render(request, template, context)