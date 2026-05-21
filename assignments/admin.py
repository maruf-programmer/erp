from django.contrib import admin

from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'group', 'author', 'deadline', 'created_at')
    list_filter = ('kind', 'group')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'score', 'silver_coins', 'submitted_at', 'teacher_seen_at', 'reviewed_at', 'student_seen_review_at')
    list_filter = ('status', 'assignment__group')
    search_fields = ('student__username', 'assignment__title')
