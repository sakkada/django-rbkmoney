# -*- coding:utf-8 -*-
from django.contrib import admin
from .models import RBKMoneyPayment

class RBKMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['paymentId', 'orderId',
                    'recipientAmount', 'recipientCurrency',
                    'paymentStatus', 'paymentData',
                    'userName', 'userEmail',
                    'updated_at', 'created_at',]

admin.site.register(RBKMoneyPayment, RBKMoneyPaymentAdmin)