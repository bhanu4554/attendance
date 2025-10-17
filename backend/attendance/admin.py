from django.contrib import admin
from .models import AttendanceRecord, AttendanceSession, Holiday


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'date', 'check_in_time', 'check_out_time', 'status',
        'marked_by_face_recognition', 'confidence_score'
    ]
    list_filter = [
        'status', 'marked_by_face_recognition', 'date', 'user__user_type',
        'user__department'
    ]
    search_fields = ['user__username', 'user__email', 'location']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active', 'created_by', 'location']
    list_filter = ['is_active', 'start_time', 'created_by']
    search_fields = ['name', 'location', 'description']
    date_hierarchy = 'start_time'


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'is_active']
    list_filter = ['is_active', 'date']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'