from django.conf import settings


class SimpleMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print('====== THIS IS before =====')

        response = self.get_response(request)

        print('====== THIS IS after =====')
        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            print('====== THIS IS exception process =====')
            print('EXCEPTION NAME: {}'.format(exception.__class__.__name__))
            print('EXCEPTION MESSAGE: {}'.format(exception.message))
        return None
