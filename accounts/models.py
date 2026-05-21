from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Bosh admin'
        TEACHER = 'teacher', 'Oqituvchi'
        ASSISTANT = 'assistant', 'Yordamchi oqituvchi'
        STUDENT = 'student', 'Oquvchi'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=30, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_login_method = models.CharField(max_length=30, blank=True)

    def is_academic_staff(self):
        return self.role in {self.Role.TEACHER, self.Role.ASSISTANT} or self.is_superuser

    def is_online(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen <= timezone.timedelta(minutes=5)

    def __str__(self):
        return self.get_full_name() or self.username


class LoginActivity(models.Model):
    class Method(models.TextChoices):
        PASSWORD = 'password', 'Parol'
        FACE_ID = 'face_id', 'Face ID'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities')
    method = models.CharField(max_length=30, choices=Method.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_method_display()} - {self.created_at:%Y-%m-%d %H:%M}'
