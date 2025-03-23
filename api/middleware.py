# middleware.py
import json
import time
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RequestLogMiddleware(MiddlewareMixin):
    """Log all requests and responses"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'remote_address': request.META.get('REMOTE_ADDR'),
                'server_hostname': request.META.get('SERVER_NAME'),
                'request_method': request.method,
                'request_path': request.get_full_path(),
                'response_status': response.status_code,
                'duration': duration,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Log user if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                log_data['user'] = request.user.username
                
            # Don't log media/static file requests
            if not any(path in request.path for path in ['/media/', '/static/']):
                logger.info(f"Request: {json.dumps(log_data)}")
                
        return response

class ActivityTrackingMiddleware(MiddlewareMixin):
    """Track user's last activity time"""
    
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Update last active time in user profile or session
            request.session['last_activity'] = timezone.now().isoformat()
        
        return response