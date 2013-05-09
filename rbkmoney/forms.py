# -*- coding: utf-8 -*-
import hashlib, decimal
from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator, validate_email
from django.core.urlresolvers import reverse
from . import conf, utils, models

hidden = {'widget': forms.HiddenInput,}

class BaseRBKMoneyFormMixin(object):
    def get_user_fields_items(self):
        # get keys/values of userFields
        result, index = [], -1
        while True:
            index += 1
            field = self.fields.get('userField_%s' % index, None)
            if not field:
                if index > 9: break
                else: continue
            result.append(('userField_%s' % index, field.initial))

        return result

    def generate_user_fields(self, values):
        # generate userFields form fields
        for index, value in enumerate(values):
            if value is None: continue
            self.fields['userField_%s' % index] = forms.CharField(initial=value,
                                                                  **hidden)

    def generate_hash_value(self, keys=None):
        # generate hash value from initial or received values
        if not keys: return u''

        values = []
        for key in keys:
            if key == 'userFields':
                values += [f[1] for f in self.get_user_fields_items()] or [u'']
            elif key == 'secretKey':
                values.append(conf.SECRET_KEY)
            else:
                # get formatted by widget values
                value = self[key].value()
                value = value and self.fields[key].widget._format_value(value)
                values.append(value or u'')

        # get hasher and hex value
        hasher = hashlib.md5 if conf.HASH_CHECK == 'MD5' else hashlib.sha512
        values = u'::'.join([unicode(i) for i in values])
        return hasher(values.encode('utf8')).hexdigest()

class RequestRBKMoneyForm(forms.Form, BaseRBKMoneyFormMixin):
    # required fields are: eshopId, recipientAmount, recipientCurrency
    # hash value will generate automatically if conf.HASH_CHECK
    action = conf.FROM_ACTION

    eshopId = forms.IntegerField(initial=conf.SHOP_ID, **hidden)
    orderId = forms.IntegerField(required=False, **hidden)

    serviceName = forms.CharField(required=False, max_length=255, **hidden)

    recipientAmount = forms.DecimalField(max_digits=9, decimal_places=2, **hidden)
    recipientCurrency = forms.ChoiceField(choices=models.CURRENCY_CHOICES,
                                          initial='RUR', **hidden)

    user_email = forms.EmailField(required=False, max_length=100, **hidden)

    # redirect urls
    successUrl = forms.CharField(max_length=255, required=False, **hidden)
    failUrl = forms.CharField(max_length=255, required=False, **hidden)

    # security hash value
    hash = forms.CharField(max_length=255, required=False, **hidden)

    # default values (preference commented because of RBK work incorrectly
    # when received empty value, so RBK required real value or nothing at all)
    version = forms.IntegerField(initial=1, required=False, **hidden)
    direct = forms.CharField(initial='false', required=False, **hidden)
    # preference = forms.CharField(initial='', required=False, **hidden)
    language = forms.CharField(initial='ru', required=False, **hidden)

    def __init__(self, *args, **kwargs):
        super(RequestRBKMoneyForm, self).__init__(*args, **kwargs)

        # localize recipientAmount
        field = self.fields['recipientAmount']
        if isinstance(field, forms.DecimalField):
            field.localize = True
            field.widget.is_localized = True

        # generate userFields fields
        if 'userFields' in kwargs.get('initial', {}):
            self.generate_user_fields(kwargs['initial']['userFields'] or [])

        # prepare initial values
        initial = kwargs.get('initial', None)
        initial and self.prepare_initials(initial)

        # generate hash value if allowed
        if conf.HASH_CHECK:
            self.fields['hash'].initial = self.generate_hash_value()

    def prepare_initials(self, initial):
        """note: prepare only form initials, not field initial"""
        amount = initial.get('recipientAmount', None)
        if amount:
            amount = amount if isinstance(amount, decimal.Decimal) \
                            else decimal.Decimal(str(amount))
            amount = amount.quantize(decimal.Decimal('.01'),
                                     rounding=decimal.ROUND_DOWN)
            initial['recipientAmount'] = amount

        successUrl = initial.get('successUrl', None)
        if successUrl is None:
            initial['successUrl'] = utils.build_absolute_uri(reverse('rbkmoney_success'))

        successUrl = initial.get('failUrl', None)
        if successUrl is None:
            initial['failUrl'] = utils.build_absolute_uri(reverse('rbkmoney_fail'))

    def generate_hash_value(self):
        keys = [u'eshopId', u'recipientAmount',
                u'recipientCurrency', u'user_email',
                u'serviceName', u'orderId',
                u'userFields', u'secretKey',]
        return super(RequestRBKMoneyForm, self).generate_hash_value(keys=keys)

class ResultRBKMoneyForm(forms.ModelForm, BaseRBKMoneyFormMixin):
    hash = forms.CharField(max_length=255, required=True)

    class Meta:
        model = models.RBKMoneyPayment
        fields = ['eshopId', 'paymentId', 'orderId', 'eshopAccount',
                  'serviceName', 'recipientAmount', 'recipientCurrency',
                  'paymentStatus', 'paymentData', 'userName', 'userEmail',]

    def __init__(self, *args, **kwargs):
        super(ResultRBKMoneyForm, self).__init__(*args, **kwargs)
        self.generate_user_fields()
        for key, field in self.fields.items():
            field.widget = forms.HiddenInput()

    def generate_user_fields(self):
        fields, index = [], -1
        while True:
            index += 1
            field = self.data.get('userField_%s' % index, None)
            if not field:
                if index > 9: break
            fields.append(field)

        super(ResultRBKMoneyForm, self).generate_user_fields(fields)

    def generate_hash_value(self):
        keys = ['eshopId', 'orderId', 'serviceName',
                'eshopAccount', 'recipientAmount',
                'recipientCurrency', 'paymentStatus',
                'userName', 'userEmail', 'paymentData',
                'secretKey',]
        return super(ResultRBKMoneyForm, self).generate_hash_value(keys=keys)

    def clean_hash(self):
        hash = self.cleaned_data['hash']
        if conf.HASH_CHECK and hash and hash != self.generate_hash_value():
            raise forms.ValidationError('Hash value is incorrect.')
        return hash