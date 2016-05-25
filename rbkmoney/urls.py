# - coding: utf-8 -
from django.conf.urls import url

from rbkmoney import views as rbkmoney_views

urlpatterns = [
    url(r'^result/$', rbkmoney_views.result, name='rbkmoney_result'),
    url(r'^success/$', rbkmoney_views.success, name='rbkmoney_success'),
    url(r'^fail/$', rbkmoney_views.fail, name='rbkmoney_fail'),
]

