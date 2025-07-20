from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP
from django.db.models import Count

@shared_task
def detect_suspicious_ips():
    # Check for high request volumes
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Get IPs with more than 100 requests in the last hour
    high_volume_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(count=Count('id'))
        .filter(count__gt=100)
    )
    
    for entry in high_volume_ips:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry['ip_address'],
            defaults={'reason': f'High request volume: {entry["count"]} in last hour'}
        )
    
    # Check for access to sensitive paths
    sensitive_paths = ['/admin/', '/login/', '/wp-admin/']
    sensitive_access = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
        .values('ip_address')
        .distinct()
    )
    
    for entry in sensitive_access:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry['ip_address'],
            defaults={'reason': f'Access to sensitive path: {entry["path"]}'}
        )
    
    return f"Detected {len(high_volume_ips)} high-volume IPs and {len(sensitive_access)} sensitive-access IPs"