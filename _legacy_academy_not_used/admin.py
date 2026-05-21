from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AdmissionApplication, Assignment, Course, Group, Salary, Submission, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil va rol', {'fields': ('role', 'phone', 'passport_number', 'birth_date', 'address', 'photo', 'bio')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration_months', 'is_active')
    search_fields = ('title',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher', 'start_date', 'lesson_time', 'is_active')
    list_filter = ('course', 'is_active')
    filter_horizontal = ('assistants', 'students')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'group', 'author', 'deadline', 'created_at')
    list_filter = ('kind', 'group')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'score', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'base_amount', 'bonus', 'penalty', 'total', 'paid')
    list_filter = ('paid', 'month')


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'course', 'status', 'created_at')
    list_filter = ('status', 'course', 'created_at')
    search_fields = ('full_name', 'phone', 'course')
