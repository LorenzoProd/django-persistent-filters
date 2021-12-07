from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings


class PersistentFiltersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path_info
        if path not in settings.PERSISTENT_FILTERS_URLS:
            return response

        query_string = request.META['QUERY_STRING']
        if 'reset-filters' in request.META['QUERY_STRING']:
            response = redirect(path)
            response.delete_cookie('filters{}'.format(path.replace('/', '_')))
            return response

        if len(query_string) > 0:
            response.set_cookie(
                key='filters{}'.format(path.replace('/', '_')),
                value=query_string,
                max_age=28800
            )
            return response

        if len(query_string) == 0 and request.COOKIES.get('filters{}'.format(path.replace('/', '_'))):
            redirect_to = request.path + '?' + request.COOKIES.get('filters{}'.format(path.replace('/', '_')))
            return HttpResponseRedirect(redirect_to)

        return response
