from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone

ALLOWED_FILE_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt',
    'zip', 'rar', '7z', 'jpg', 'jpeg', 'png', 'gif', 'webp',
    'mp3', 'wav', 'mp4', 'mov', 'avi', 'mkv',
    'py', 'js', 'ts', 'html', 'css', 'json', 'sql', 'ipynb',
]


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

    def is_academic_staff(self):
        return self.role in {self.Role.TEACHER, self.Role.ASSISTANT} or self.is_superuser

    def __str__(self):
        full_name = self.get_full_name()
        return full_name or self.username


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
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, related_name='teaching_groups', limit_choices_to={'role': User.Role.TEACHER})
    assistants = models.ManyToManyField(User, blank=True, related_name='assistant_groups', limit_choices_to={'role': User.Role.ASSISTANT})
    students = models.ManyToManyField(User, blank=True, related_name='student_groups', limit_choices_to={'role': User.Role.STUDENT})
    start_date = models.DateField(default=timezone.now)
    lesson_days = models.CharField(max_length=120, blank=True, help_text='Masalan: Dushanba, Chorshanba, Juma')
    lesson_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.course.title} - {self.name}'


class Assignment(models.Model):
    class Kind(models.TextChoices):
        HOMEWORK = 'homework', 'Uyga vazifa'
        EXAM = 'exam', 'Imtihon'

    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.HOMEWORK)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='assignments')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_assignments')
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
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', limit_choices_to={'role': User.Role.STUDENT})
    text = models.TextField(blank=True)
    file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)],
    )
    score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f'{self.student} - {self.assignment}'


class Salary(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    month = models.DateField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.base_amount + self.bonus - self.penalty

    def __str__(self):
        return f'{self.employee} - {self.month:%Y-%m}'


class AdmissionApplication(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Yangi'
        CONTACTED = 'contacted', 'Bog‘lanildi'
        ACCEPTED = 'accepted', 'Qabul qilindi'
        REJECTED = 'rejected', 'Rad etildi'

    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=30)
    course = models.CharField(max_length=120)
    age = models.PositiveIntegerField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} - {self.course}'
