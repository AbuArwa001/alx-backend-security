from django.contrib.auth.views import LoginView
from django_ratelimit.decorators import ratelimit

class CustomLoginView(LoginView):
    @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)