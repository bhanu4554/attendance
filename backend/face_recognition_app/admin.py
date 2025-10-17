from django.contrib import admin
from .models import FaceEncoding, FaceRecognitionLog


@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    list_display = ['user', 'confidence_threshold', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['encoding_data', 'created_at', 'updated_at']


@admin.register(FaceRecognitionLog)
class FaceRecognitionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'confidence_score', 'location', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['user__username', 'location']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'