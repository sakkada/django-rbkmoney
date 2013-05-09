# - coding: utf-8 -
from django.conf import settings

# идентификационные данные (обязательны к заполнению)
SHOP_ID = getattr(settings, 'RBKMONEY_SHOP_ID', None)
SECRET_KEY = getattr(settings, 'RBKMONEY_SECRET_KEY', None)

# использовать ли hash при проверке данных
HASH_CHECK = getattr(settings, 'RBKMONEY_HASH_CHECK', None)
HASH_CHECK = HASH_CHECK in ['MD5', 'SHA512'] and HASH_CHECK \
                        or (HASH_CHECK and 'MD5')

# url, на который отправляется форма запроса
FROM_ACTION = getattr(settings, 'RBKMONEY_ACTION',
                                'https://rbkmoney.ru/acceptpurchase.aspx')

# протокол (http или https), используемый при гереарции ссылок success и fail
URI_PROTOCOL = getattr(settings, 'RBKMONEY_URI_PROTOCOL', None)
URI_PROTOCOL = URI_PROTOCOL in ['http', 'https'] and URI_PROTOCOL or 'http'

if not (SHOP_ID and SECRET_KEY):
    raise ValueError('Не указаны обязательные параметры конфигурации RBK Money'
                     ' (RBKMONEY_SHOP_ID, RBKMONEY_SECRET_KEY).')