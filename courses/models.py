from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    duration_months = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Group(models.Model):
    name = models.CharField(max_length=80)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='groups')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='teaching_groups')
    assistants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assistant_groups')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='student_groups')
    start_date = models.DateField(default=timezone.now)
    lesson_days = models.CharField(max_length=120, blank=True, help_text='Masalan: Dushanba, Chorshanba, Juma')
    lesson_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.course.title} - {self.name}'
