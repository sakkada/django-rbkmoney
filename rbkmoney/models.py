# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

STATUS_CHOICES = [
    # (0, u'Операция создана',),
    (3, u'Операция принята на обработку',),
    (5, u'Операция исполнена',),
    # (8, u'Ошибка исполнения операции',),
    # (9, u'Операция отменена',),
]

CURRENCY_CHOICES = [
    (u'USD', u'USD',),
    (u'RUR', u'RUR',),
    (u'EUR', u'EUR',),
    (u'UAH', u'UAH',),
]

class RBKMoneyPayment(models.Model):
    # все поля кроме orderId, serviceName, userName и userEmail обязательны

    eshopId = models.IntegerField(u'Id магазина участника')
    paymentId = models.IntegerField(u'Идентификатор операции в системе RBK Money')
    orderId = models.IntegerField(u'Номер заказа', blank=False, null=True)
    eshopAccount = models.CharField(u'Идентификатор учетной записи Участника',
                                    max_length=50)

    serviceName = models.CharField(u'Назначение операции',
                                   max_length=300, blank=True)
    recipientAmount = models.DecimalField(u'Сумма платежа',
                                          decimal_places=2, max_digits=8)
    recipientCurrency = models.CharField(u'Валюта платежа', max_length=10,
                                         choices=CURRENCY_CHOICES, default='RUR')

    paymentStatus = models.IntegerField(u'Статус', choices=STATUS_CHOICES)
    paymentData = models.DateTimeField(u'Дата и время исполнения операции')

    userName = models.CharField(u'Имя Пользователя в Системе RBK Money',
                                max_length=255, blank=True)
    userEmail = models.CharField(u'Email Пользователя в Системе RBK Money',
                                 max_length=255, blank=True)

    updated_at = models.DateTimeField(u'Дата и время обновления', auto_now=True)
    created_at = models.DateTimeField(u'Дата и время получения уведомления',
                                      default=timezone.now, editable=False)

    def __unicode__(self):
        return u"{0} | {1} | {2}".format(self.id, self.recipientAmount,
                                                  self.paymentStatus)