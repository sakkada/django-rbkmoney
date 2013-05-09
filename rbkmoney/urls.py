# - coding: utf-8 -
from django.conf.urls import patterns, include, url

urlpatterns = patterns('rbkmoney.views',
    url(r'^result/$', 'result', name='rbkmoney_result'),
    url(r'^success/$', 'success', name='rbkmoney_success'),
    url(r'^fail/$', 'fail', name='rbkmoney_fail'),
)