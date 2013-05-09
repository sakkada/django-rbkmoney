# - coding: utf-8 -
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from . import forms, signals

from django.utils.log import getLogger

# get system logger
logger = getLogger('rbkmoney')

@csrf_exempt
def result(request):
    """Оповещение о переводе."""
    logger.debug(request.POST)
    logger.debug(request.GET)
    logger.debug(request)

    form = forms.ResultRBKMoneyForm(request.POST or None)
    if form.is_valid():
        # сохранение данных о переводе в базу
        payment = form.save()

        # дополнительные действия с заказом производятся
        # в обработчике сигнала rbkmoney.signals.result_received
        signals.result_received.send(sender=payment,
                                     user_fields=form.get_user_fields_items())

        # для обеих версий протокола и header 200 OK и строка OK
        return HttpResponse('OK')

    # в случае успеха система ждет 200 OK, поэтому здесь 500 Bad Request
    return HttpResponseBadRequest('FAIL')

@csrf_exempt
def success(request, template_name='rbkmoney/success.html', extra_context=None):
    """Обработчик для SuccessURL"""

    logger.debug(request.POST)
    logger.debug(request.GET)
    logger.debug(request)

    return TemplateResponse(request, template_name, extra_context)

@csrf_exempt
def fail(request, template_name='rbkmoney/fail.html', extra_context=None):
    """Обработчик для FailURL"""

    logger.debug(request.POST)
    logger.debug(request.GET)
    logger.debug(request)

    return TemplateResponse(request, template_name, extra_context)