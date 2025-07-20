import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_security.settings')

app = Celery('app_security')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'detect-suspicious-ips-hourly': {
        'task': 'ip_tracking.tasks.detect_suspicious_ips',
        'schedule': crontab(minute=0),  # every hour
    },
}
