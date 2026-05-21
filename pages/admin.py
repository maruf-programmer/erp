from django.contrib import admin

from .models import FeaturedPerson, HomePageSettings, VideoLesson


@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'students_metric', 'teachers_metric', 'updated_at')


@admin.register(FeaturedPerson)
class FeaturedPersonAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'kind', 'title', 'is_active', 'order')
    list_filter = ('kind', 'is_active')
    search_fields = ('full_name', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'teacher__username', 'teacher__first_name', 'teacher__last_name')
