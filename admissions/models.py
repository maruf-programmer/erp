from django.db import models


class AdmissionApplication(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Yangi'
        CONTACTED = 'contacted', 'Bog‘lanildi'
        ACCEPTED = 'accepted', 'Qabul qilindi'
        REJECTED = 'rejected', 'Rad etildi'

    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=30)
    application_type = models.CharField(max_length=120, default='O‘quvchi arizasi')
    course = models.CharField(max_length=120)
    age = models.PositiveIntegerField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} - {self.course}'
