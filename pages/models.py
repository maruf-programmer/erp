from django.conf import settings
from django.db import models


class HomePageSettings(models.Model):
    title = models.CharField(max_length=180, default='Kelajakdagi kasbingizni kuchli IT ustozlar bilan boshlang.')
    subtitle = models.TextField(default='Nova Academy o‘quvchilarni real loyiha asosida tayyorlaydi.')
    hero_badge = models.CharField(max_length=120, default='2026 yil qabuli davom etmoqda')
    students_metric = models.PositiveIntegerField(default=10000)
    teachers_metric = models.PositiveIntegerField(default=28)
    groups_metric = models.PositiveIntegerField(default=86)
    courses_metric = models.PositiveIntegerField(default=12)
    founder_name = models.CharField(max_length=140, default='Maruf Amonturdiyev')
    founder_quote = models.TextField(default='Maqsadimiz yoshlarni xalqaro darajadagi IT mutaxassisga aylantirish.')
    founder_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    grant_text = models.CharField(max_length=220, default='Eng faol o‘quvchilar uchun 30% gacha chegirma va stajirovka tavsiyasi.')
    telegram = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Home page sozlamasi'
        verbose_name_plural = 'Home page sozlamalari'

    def __str__(self):
        return 'Home page sozlamalari'


class FeaturedPerson(models.Model):
    class Kind(models.TextChoices):
        BEST_STUDENT = 'best_student', 'Eng yaxshi o‘quvchi'
        TEACHER_OF_YEAR = 'teacher_of_year', 'Yil o‘qituvchisi'
        TEACHER = 'teacher', 'Ustoz'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    kind = models.CharField(max_length=30, choices=Kind.choices)
    full_name = models.CharField(max_length=160, blank=True)
    title = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='featured/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'full_name']

    @property
    def display_name(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.full_name

    def __str__(self):
        return self.display_name


class VideoLesson(models.Model):
    title = models.CharField(max_length=180)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='video_lessons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
