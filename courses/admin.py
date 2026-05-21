from django.contrib import admin

from .models import Course, Group


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration_months', 'is_active')
    search_fields = ('title',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher', 'start_date', 'lesson_time', 'is_active')
    list_filter = ('course', 'is_active')
    filter_horizontal = ('assistants', 'students')
