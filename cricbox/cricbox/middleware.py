from django.http import HttpResponse


class HealthCheckMiddleware:
    """Answer /healthz before anything else runs.

    Platform health checkers (Fly.io, and likely Render too) hit the app
    directly on its internal address rather than through the public
    hostname, so the Host header is something like '172.19.2.50:8000' —
    not a value we can predict or whitelist in ALLOWED_HOSTS, since it's a
    different, dynamically-assigned IP per Machine/instance.

    Placed first in MIDDLEWARE, this runs before SecurityMiddleware (which
    is what raises DisallowedHost) and before anything else that cares about
    the Host header, HTTPS, or CSRF. A liveness ping doesn't need any of
    that — it should just work.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthz":
            return HttpResponse("ok")
        return self.get_response(request)
