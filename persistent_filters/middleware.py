from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings


class PersistentFiltersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _filter_query_string(self, query_string):
        excluded_params = getattr(settings, 'EXCLUDED_FILTER_PARAMS', ['_export'])
        parsed_qs = urllib.parse.parse_qs(query_string)
        parsed_qs = {key: value for key, value in parsed_qs.items() if key not in excluded_params}
        filtered_query_string = urllib.parse.urlencode(parsed_qs, doseq=True)
        return filtered_query_string

    def _set_filters(self):
        if self.use_session:
            self.request.session[self.key] = self.query_string
            return
        self.response.set_cookie(
            key=self.key,
            value=self.query_string,
            max_age=28800
        )

    def _delete_filters(self):
        self.response = redirect(self.path)
        if self.use_session:
            if not self.request.session.get(self.key):
                return
            self.request.session.pop(self.key)
            return
        self.response.delete_cookie(self.key)

    def _key_is_set(self):
        if self.use_session:
            return self.request.session.get(self.key)
        return self.request.COOKIES.get(self.key)

    def _get_redirect_url(self):
        if self.use_session:
            return self.request.path + '?' + self.request.session.get(self.key)
        return self.request.path + '?' + self.request.COOKIES.get(self.key)

    def __call__(self, request):
        if hasattr(settings, 'PERSISTENT_FILTERS_IN_REQUEST'):
            raise Exception("PERSISTENT_FILTERS_IN_REQUEST deprecated. Use PERSISTENT_FILTERS_IN_SESSION instead.")
        self.use_session = False
        if hasattr(settings, 'PERSISTENT_FILTERS_IN_SESSION'):
            self.use_session = getattr(settings, 'PERSISTENT_FILTERS_IN_SESSION')
        self.request = request
        self.response = self.get_response(self.request)
        self.path = request.path_info
        self.key = 'filters{}'.format(self.path.replace('/', '_'))

        if self.path not in settings.PERSISTENT_FILTERS_URLS:
            return self.response

        self.query_string = self._filter_query_string(request.META['QUERY_STRING'])

        if 'reset-filters' in self.query_string:
            self._delete_filters()
            return self.response

        if len(self.query_string) > 0:
            self._set_filters()
            return self.response

        if len(self.query_string) == 0 and self._key_is_set():
            redirect_to = self._get_redirect_url()
            return HttpResponseRedirect(redirect_to)

        return self.response
