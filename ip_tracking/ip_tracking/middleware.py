"""
middleware class that logs request details.
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging
from ip_tracking.models import BlockedIP, RequestLog
from django.utils import timezone

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log request details.
    """
    def process_request(self, request):
        """
        Log the request details.
        """
        try:
            # Create a new RequestLog entry
            RequestLog.objects.create(
                method=request.method,
                path=request.get_full_path(),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                timestamp=timezone.now()
            )
        except Exception as e:
            logging.error(f"Error logging request: {e}")

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP address has been blocked.")
        
        cache_key = f'geo_{ip_address}'
        geodata = cache.get(cache_key)

        if not geodata:
            geodata = self.geo_api.get_geolocation(ip_address)
            cache.set(cache_key, geodata, 86400)

        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            country=geodata.get('country_name'),
            city=geodata.get('city')
        )

        return self.get_response(request)