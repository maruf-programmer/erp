from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .activity import record_login_activity
from .models import LoginActivity


@receiver(user_logged_in)
def save_password_login(sender, request, user, **kwargs):
    if getattr(request, '_skip_password_activity', False):
        return
    record_login_activity(request, user, LoginActivity.Method.PASSWORD)
