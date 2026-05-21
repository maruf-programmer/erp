from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from courses.models import Group

ALLOWED_FILE_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt',
    'zip', 'rar', '7z', 'jpg', 'jpeg', 'png', 'gif', 'webp',
    'mp3', 'wav', 'mp4', 'mov', 'avi', 'mkv',
    'py', 'js', 'ts', 'html', 'css', 'json', 'sql', 'ipynb',
]


class Assignment(models.Model):
    class Kind(models.TextChoices):
        HOMEWORK = 'homework', 'Uyga vazifa'
        EXAM = 'exam', 'Imtihon'

    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.HOMEWORK)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='assignments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_assignments')
    description = models.TextField()
    file = models.FileField(
        upload_to='assignments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)],
    )
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

    def __str__(self):
        return self.title


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Tekshirilmagan'
        ACCEPTED = 'accepted', 'Qabul qilindi'
        REJECTED = 'rejected', 'Qaytarildi'

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    text = models.TextField(blank=True)
    file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)],
    )
    score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    silver_coins = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    feedback = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_submissions',
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    teacher_seen_at = models.DateTimeField(blank=True, null=True)
    student_seen_review_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('assignment', 'student')

    @property
    def has_work(self):
        return bool(self.text.strip() or self.file)

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.deadline

    def __str__(self):
        return f'{self.student} - {self.assignment}'
