import time
from django.utils.deprecation import MiddlewareMixin
from .models import VisitorProfile
from django.utils.timezone import now
from pytz import timezone

NYC_TIMEZONE = timezone('America/New_York')

class AnalyticsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.start_time = time.time()
        if not request.session.session_key:
            request.session.save()
        
        session_id = request.session.session_key
        if session_id:
            visitor_profiles = VisitorProfile.all()
            visitor_profile_exists = any(profile.session_id == session_id for profile in visitor_profiles)

            if not visitor_profile_exists:
                request.session['is_new_profile_needed'] = True
            else:
                request.session['is_new_profile_needed'] = False

    def process_response(self, request, response):
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        if request.path_info.startswith('/track_analytics/') or request.path_info.startswith('/media/'):
            return response

        if request.session.get('is_new_profile_needed'):
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_type = self._get_device_type(user_agent)  
            country = request.META.get('HTTP_CF_IPCOUNTRY', 'Unknown')
            region = request.POST.get('region', 'Unknown')
            utm_source = request.POST.get('utm_source', '')

            new_profile = VisitorProfile(
                session_id=session_id,
                ip_address=ip_address,
                utm_source=utm_source,
                user_agent=user_agent,
                device_type=device_type,
                country=country,
                region=region,
                page_urls=[],
                scroll_depth=[],
                time_spent=[]
            )
            new_profile.save()

            request.session['is_new_profile_needed'] = False

        return response

    def _get_device_type(self, user_agent):
        """Determines the device type based on the user-agent string."""
        if 'Mobile' in user_agent:
            return 'Mobile'
        elif 'Tablet' in user_agent:
            return 'Tablet'
        return 'Desktop'

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
