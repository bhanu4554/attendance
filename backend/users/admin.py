from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'employee_id', 'student_id', 
                   'department', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'department', 'created_at']
    search_fields = ['username', 'email', 'employee_id', 'student_id', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'employee_id', 'student_id', 'phone_number', 
                      'department', 'profile_image')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'employee_id', 'student_id', 'phone_number', 
                      'department', 'profile_image')
        }),
    )