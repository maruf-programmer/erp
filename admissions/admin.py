from django.contrib import admin

from .models import AdmissionApplication


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'application_type', 'course', 'status', 'created_at')
    list_filter = ('status', 'application_type', 'course', 'created_at')
    search_fields = ('full_name', 'phone', 'course', 'application_type')
