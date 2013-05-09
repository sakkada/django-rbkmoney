from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^rbkmoney/', include('rbkmoney.urls')),
    url(r'^orders/', include('orderapp.urls')),
)