from django.http.response import Http404
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext
from django.urls import resolve, Resolver404
from django.conf import settings

from is_core.exceptions import ResponseException
from is_core.exceptions.response import response_exception_factory
from is_core.utils.compatibility import MiddlewareMixin


def get_request_kwargs(request):
    try:
        return resolve(request.path).kwargs
    except Resolver404:
        return {}


class RequestKwargsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.kwargs = get_request_kwargs(request)


# Not working with pyston exceptions
class HttpExceptionsMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, ResponseException):
            return exception.get_response(request)
        if isinstance(exception, ValidationError):
            return response_exception_factory(request, 422, gettext('Unprocessable Entity'), exception.messages)
        if not settings.DEBUG and isinstance(exception, Http404):
            return response_exception_factory(request, 404, gettext('Not Found'), force_str(exception))
