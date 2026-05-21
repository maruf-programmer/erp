from django.contrib import admin

from .models import Salary


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'base_amount', 'bonus', 'penalty', 'total', 'paid')
    list_filter = ('paid', 'month')
