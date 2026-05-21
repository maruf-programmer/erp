from django.utils import timezone

from .models import LoginActivity


def client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def record_login_activity(request, user, method):
    LoginActivity.objects.create(
        user=user,
        method=method,
        ip_address=client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    user.last_login_method = method
    user.last_seen = timezone.now()
    user.save(update_fields=['last_login_method', 'last_seen'])
