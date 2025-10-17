from django.contrib import admin
from .models import (
    AcademicYear, Department, Class, Section, Student, 
    Subject, ClassSubject
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date']
    search_fields = ['name']
    ordering = ['-start_date']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_of_department', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'department', 'grade_level', 'academic_year', 
        'class_teacher', 'total_students', 'is_active'
    ]
    list_filter = ['department', 'academic_year', 'grade_level', 'is_active']
    search_fields = ['name', 'department__name']
    ordering = ['department', 'grade_level', 'name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'class_obj', 'section_teacher', 'current_students', 
        'max_students', 'room_number', 'is_active'
    ]
    list_filter = ['class_obj__department', 'is_active']
    search_fields = ['name', 'class_obj__name', 'room_number']
    ordering = ['class_obj', 'name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'full_name', 'roll_number', 'class_obj', 
        'section', 'admission_date', 'is_active'
    ]
    list_filter = [
        'class_obj__department', 'class_obj', 'section', 'gender', 
        'is_active', 'admission_date'
    ]
    search_fields = [
        'student_id', 'roll_number', 'user__first_name', 
        'user__last_name', 'user__email'
    ]
    ordering = ['class_obj', 'section', 'roll_number']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['user', 'student_id', 'roll_number', 'class_obj', 'section']
        }),
        ('Personal Details', {
            'fields': ['date_of_birth', 'gender', 'blood_group', 'address']
        }),
        ('Guardian Information', {
            'fields': ['guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relation']
        }),
        ('Academic Information', {
            'fields': ['admission_date', 'previous_school']
        }),
        ('Additional Services', {
            'fields': ['transport_required', 'hostel_required']
        }),
        ('Status', {
            'fields': ['is_active']
        })
    ]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'credit_hours', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['department', 'name']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'subject', 'teacher', 'is_active']
    list_filter = ['class_obj__department', 'subject', 'is_active']
    search_fields = ['class_obj__name', 'subject__name', 'teacher__username']
    ordering = ['class_obj', 'subject']