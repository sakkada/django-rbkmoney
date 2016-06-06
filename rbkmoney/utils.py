try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    # Django < 1.9 support.
    from django.contrib.sites.models import get_current_site

from . import conf

def build_absolute_uri(url, request=None):
    return ''.join([conf.URI_PROTOCOL, '://',
                    get_current_site(request).domain, url])

