"""
middleware class that logs request details.
"""
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
        
        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP address has been blocked.")