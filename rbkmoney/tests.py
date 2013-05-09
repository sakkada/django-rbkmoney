# - coding: utf-8 -
from unittest import TestCase
from decimal import Decimal
from django.test import TestCase as DjangoTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from . import utils, signals, models, forms, conf

class RBKMoneyRequestFormTest(TestCase):

    REQUEST_DICTS = {
        'request': {
            'eshopId': 2000005,
            'orderId': 1234,
            'serviceName': u' Книга',
            'recipientAmount': Decimal('12.30'),
            'recipientCurrency': u'RUR',
            'user_email': u'admin@rbkmoney.ru',
            'userFields': None,
        },
        'result': {
            'eshopId' :"2000005",
            'paymentId' :"2007022292",
            'orderId' :"1234",
            'eshopAccount' :"RU123456789",
            'serviceName' :"Kniga",
            'recipientAmount' :"12.30",
            'recipientCurrency' :"RUR",
            'paymentStatus' :"5",
            'userName' :"Petrov Alexander",
            'userEmail' :"admin@rbkmoney.ru",
            'paymentData' :"2007-10-28 14:22:35",
            'secretKey' :"myKey",
            'hash': "5cebada7c46e2e944db5a90e2a4f7f5a",
            'userField_1':"value_1",
            'userField_2':"value_2",
        },
        'default': {
            'orderId': 77,
            'serviceName': u'Два колеса, руль, педали и мешок свободы.',
            'recipientAmount': Decimal('10.57'),
            'recipientCurrency': u'RUR',
            'user_email': u'some@email.com',
            'userFields': ['some', 'values', 'list',],
        },
        'non_zero_indexed': {
            'orderId': 77,
            'serviceName': u'any',
            'recipientAmount': Decimal('1.01'),
            'recipientCurrency': u'RUR',
            'user_email': u'some@email.com',
            'userFields': [None, 'some', None, 'values', 'list',],
        },
    }

    def setUp(self):
        conf.SECRET_KEY = u'myKey'
        conf.HASH_CHECK = u'MD5'

    def testRequestUserFieldsGeneration(self):
        form = forms.RequestRBKMoneyForm(initial=self.REQUEST_DICTS['default'])

        # test user fields generation
        self.assertEqual(all('userField_%s' % i in form.fields
                             for i in range(0,3)), True)

        # test user fields values
        self.assertEqual(form.fields['userField_0'].initial, form['userField_0'].value())
        self.assertEqual(form.fields['userField_1'].initial, form['userField_1'].value())
        self.assertEqual(form.fields['userField_2'].initial, form['userField_2'].value())

        # test user fields values getter
        self.assertEqual(form.get_user_fields_items(), [('userField_0', 'some'),
                                                        ('userField_1', 'values'),
                                                        ('userField_2', 'list'),])

        # test non zero indexed userFields and not consistent
        form = forms.RequestRBKMoneyForm(initial=self.REQUEST_DICTS['non_zero_indexed'])
        self.assertEqual(form.get_user_fields_items(), [('userField_1', 'some'),
                                                        ('userField_3', 'values'),
                                                        ('userField_4', 'list'),])

    def testRequestHashValueGeneration(self):
        # example taken from rmbmoney api pdf document
        form = forms.RequestRBKMoneyForm(initial=self.REQUEST_DICTS['request'])
        self.assertEqual(form.generate_hash_value(), 'bfb59b33db4c7fafa4c6d2bfaec02ec2')

    def testRequestInitialValuesProcessing(self):
        # test recipientAmount Decimal quantizing and eshopId redefining
        form = forms.RequestRBKMoneyForm(initial={'eshopId': 999,
                                                  'recipientAmount': Decimal('10.77'),
                                                  'recipientCurrency': u'RUR',})

        self.assertEqual(form['recipientAmount'].value(), Decimal('10.77'))
        self.assertEqual(form['eshopId'].value(), 999)

        form = forms.RequestRBKMoneyForm(initial={'recipientAmount': Decimal('10.772'),
                                                  'recipientCurrency': u'RUR',})

        self.assertEqual(form['recipientAmount'].value(), Decimal('10.77'))
        self.assertEqual(form['eshopId'].value(), conf.SHOP_ID)

        form = forms.RequestRBKMoneyForm(initial={'recipientAmount': Decimal('10.778'),
                                                  'recipientCurrency': u'RUR',})

        self.assertEqual(form['recipientAmount'].value(), Decimal('10.77'))

        form = forms.RequestRBKMoneyForm(initial={'recipientAmount': Decimal('10.7'),
                                                  'recipientCurrency': u'RUR',})

        self.assertEqual(form['recipientAmount'].value(), Decimal('10.70'))
        self.assertEqual(form['recipientAmount'].__str__().__contains__('value="10,70"'), True)

        # test urls defaults
        successUrl = utils.build_absolute_uri(reverse('rbkmoney_success'))
        failUrl = utils.build_absolute_uri(reverse('rbkmoney_fail'))

        form = forms.RequestRBKMoneyForm(initial={'recipientAmount': Decimal('10.7'),
                                                  'recipientCurrency': u'RUR',})

        self.assertEqual(form['successUrl'].value(), successUrl)
        self.assertEqual(form['failUrl'].value(), failUrl)

        form = forms.RequestRBKMoneyForm(initial={'recipientAmount': Decimal('10.7'),
                                                  'recipientCurrency': u'RUR',
                                                  'successUrl': u'',})

        self.assertEqual(form['successUrl'].value(), u'')
        self.assertEqual(form['failUrl'].value(), failUrl)

    def testRequestHashValueGeneration(self):
        # example taken from rmbmoney api pdf document
        form = forms.ResultRBKMoneyForm(self.REQUEST_DICTS['result'])
        self.assertEqual(form.generate_hash_value(), form['hash'].value())

    def testResultUserFieldsGeneration(self):
        form = forms.ResultRBKMoneyForm(self.REQUEST_DICTS['result'])

        # test user fields generation
        self.assertEqual(all('userField_%s' % i in form.fields
                             for i in range(1,3)), True)

        # test user fields values
        self.assertEqual(form.data['userField_1'], form['userField_1'].value())
        self.assertEqual(form.data['userField_2'], form['userField_2'].value())

        # test user fields values getter
        self.assertEqual(form.get_user_fields_items(), [('userField_1', 'value_1'),
                                                        ('userField_2', 'value_2'),])

    def testResultViewWorkflow(self):
        signals.result_received.connect(self.on_result_received)
        client, data = Client(), dict(self.REQUEST_DICTS['result'])
        self.SIGNAL_STATUS = None

        result_url = reverse('rbkmoney_result')
        success_url = reverse('rbkmoney_success')
        fail_url = reverse('rbkmoney_fail')

        # test valid data and signal calling
        response = client.post(result_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'OK')
        self.assertEqual(self.SIGNAL_STATUS, 'OK')

        # test invalid data
        data.update({'eshopId': 2000006,})
        response = client.post(result_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'FAIL')

        # test success and fail view call
        response = client.post(success_url)
        self.assertEqual(response.status_code, 200)
        response = client.post(fail_url)
        self.assertEqual(response.status_code, 200)

    def on_result_received(self, sender, **kwargs):
        user_fields = [('userField_1', u'value_1',), ('userField_2', u'value_2',)]

        if isinstance(sender, models.RBKMoneyPayment) \
            and sender.paymentStatus == 5 \
             and kwargs['user_fields'] == user_fields:
            self.SIGNAL_STATUS = 'OK'