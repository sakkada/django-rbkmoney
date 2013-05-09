from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^payment/$', 'orderapp.views.payment', name='payment'),
)