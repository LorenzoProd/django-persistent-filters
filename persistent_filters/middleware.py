from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings


class PersistentFiltersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _set_filters(self):
        if self.use_request:
            self.request.session[self.key] = self.query_string
            return
        self.response.set_cookie(
            key=self.key,
            value=self.query_string,
            max_age=28800
        )

    def _delete_filters(self):
        self.response = redirect(self.path)
        if self.use_request:
            if not self.request.session.get(self.key):
                return
            self.request.session.pop(self.key)
            return
        self.response.delete_cookie(self.key)

    def _key_is_set(self):
        if self.use_request:
            return self.request.session.get(self.key)
        return self.request.COOKIES.get(self.key)

    def _get_redirect_url(self):
        if self.use_request:
            return self.request.path + '?' + self.request.session.get(self.key)
        return self.request.path + '?' + self.request.COOKIES.get(self.key)

    def __call__(self, request):
        self.use_request = False
        if hasattr(settings, 'PERSISTENT_FILTERS_IN_REQUEST'):
            self.use_request = getattr(settings, 'PERSISTENT_FILTERS_IN_REQUEST')
        self.request = request
        self.response = self.get_response(self.request)
        self.path = request.path_info
        self.key = 'filters{}'.format(self.path.replace('/', '_'))

        if self.path not in settings.PERSISTENT_FILTERS_URLS:
            return self.response

        self.query_string = request.META['QUERY_STRING']
        if 'reset-filters' in request.META['QUERY_STRING']:
            self._delete_filters()
            return self.response

        if len(self.query_string) > 0:
            self._set_filters()
            return self.response

        if len(self.query_string) == 0 and self._key_is_set():
            redirect_to = self._get_redirect_url()
            return HttpResponseRedirect(redirect_to)

        return self.response
