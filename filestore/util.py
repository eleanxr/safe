
from functools import wraps

def http_basic_auth(func):
    """
    A decorator to allow authentication to be performed
    on a method decorated with @login_required using the
    standard HTTP Basic Authorization header.

    This has to be a decorator because it must be applied
    *before* the @login_required decorator is applied,
    otherwise @login_required's redirect would kick in
    before we have an opportunity to read the header.
    Such behavior would keep this method from being used
    as a service method.
    """
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator

class HttpStatus:
    """
    Contains common HTTP status codes.
    """
    OK = 200
    EXISTS = 302
    NOT_FOUND = 404

