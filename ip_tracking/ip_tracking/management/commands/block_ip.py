from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Add an IP address to the block list'
    
    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str)
        parser.add_argument('--reason', type=str, help='Reason for blocking')
    
    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options.get('reason', '')
        
        BlockedIP.objects.create(
            ip_address=ip_address,
            reason=reason or None
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully blocked IP: {ip_address}'))