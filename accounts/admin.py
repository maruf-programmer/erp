from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LoginActivity, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil va rol', {'fields': ('role', 'phone', 'passport_number', 'birth_date', 'address', 'photo', 'bio')}),
        ('Faollik', {'fields': ('last_seen', 'last_login_method')}),
    )
    readonly_fields = ('last_seen', 'last_login_method')
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone', 'last_login_method', 'last_seen', 'online_status', 'is_staff')
    list_filter = ('role', 'last_login_method', 'is_staff', 'is_superuser')

    @admin.display(description='Holati')
    def online_status(self, obj):
        return 'Online' if obj.is_online() else 'Offline'


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'ip_address', 'created_at')
    list_filter = ('method', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'ip_address')
    readonly_fields = ('user', 'method', 'ip_address', 'user_agent', 'created_at')
