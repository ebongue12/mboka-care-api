from django.contrib import admin
from .models import Reminder, ReminderLog

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'reminder_type', 'frequency', 'is_active', 'start_date', 'created_at']
    list_filter = ['reminder_type', 'frequency', 'is_active']
    search_fields = ['title', 'medication_name']
    date_hierarchy = 'start_date'

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['reminder', 'scheduled_datetime', 'status', 'confirmed_at']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['reminder__title', 'notes']
    date_hierarchy = 'scheduled_date'
