from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AcademicYear, Department, Class, Section, Student, 
    Subject, ClassSubject
)
from users.serializers import UserProfileSerializer

User = get_user_model()


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
        read_only_fields = ['created_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    head_of_department_details = UserProfileSerializer(
        source='head_of_department', read_only=True
    )
    total_classes = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head_of_department',
            'head_of_department_details', 'is_active', 'total_classes',
            'total_students', 'created_at'
        ]
        read_only_fields = ['created_at', 'total_classes', 'total_students']

    def get_total_classes(self, obj):
        return obj.classes.filter(is_active=True).count()

    def get_total_students(self, obj):
        return Student.objects.filter(
            class_obj__department=obj,
            is_active=True
        ).count()


class SectionSerializer(serializers.ModelSerializer):
    section_teacher_details = UserProfileSerializer(
        source='section_teacher', read_only=True
    )
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    
    class Meta:
        model = Section
        fields = [
            'id', 'name', 'class_obj', 'class_name', 'section_teacher',
            'section_teacher_details', 'max_students', 'current_students',
            'room_number', 'schedule_start_time', 'schedule_end_time',
            'is_active', 'is_full', 'created_at'
        ]
        read_only_fields = ['created_at', 'current_students', 'is_full', 'class_name']


class ClassSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)
    class_teacher_details = UserProfileSerializer(
        source='class_teacher', read_only=True
    )
    academic_year_details = AcademicYearSerializer(
        source='academic_year', read_only=True
    )
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'grade_level', 'department', 'department_details',
            'academic_year', 'academic_year_details', 'class_teacher',
            'class_teacher_details', 'total_students', 'sections',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at', 'total_students']


class SubjectSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'description', 'department',
            'department_details', 'credit_hours', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class ClassSubjectSerializer(serializers.ModelSerializer):
    class_details = ClassSerializer(source='class_obj', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)
    teacher_details = UserProfileSerializer(source='teacher', read_only=True)
    
    class Meta:
        model = ClassSubject
        fields = [
            'id', 'class_obj', 'class_details', 'subject', 'subject_details',
            'teacher', 'teacher_details', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class StudentSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)
    class_details = ClassSerializer(source='class_obj', read_only=True)
    section_details = SectionSerializer(source='section', read_only=True)
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'user_details', 'student_id', 'roll_number',
            'class_obj', 'class_details', 'section', 'section_details',
            'date_of_birth', 'gender', 'blood_group', 'address',
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relation',
            'admission_date', 'previous_school', 'transport_required',
            'hostel_required', 'full_name', 'age', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'student_id', 'full_name', 'age']

    def validate(self, attrs):
        # Validate section belongs to class
        class_obj = attrs.get('class_obj')
        section = attrs.get('section')
        
        if class_obj and section and section.class_obj != class_obj:
            raise serializers.ValidationError(
                "Selected section does not belong to the selected class"
            )
        
        # Check section capacity
        if section and section.is_full and not self.instance:
            raise serializers.ValidationError(
                f"Section {section.name} is at maximum capacity"
            )
        
        return attrs


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student with user"""
    # User fields
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = Student
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'roll_number', 'class_obj', 'section', 'date_of_birth',
            'gender', 'blood_group', 'address', 'guardian_name',
            'guardian_phone', 'guardian_email', 'guardian_relation',
            'admission_date', 'previous_school', 'transport_required',
            'hostel_required'
        ]

    def validate(self, attrs):
        # Validate section belongs to class
        class_obj = attrs.get('class_obj')
        section = attrs.get('section')
        
        if section and section.class_obj != class_obj:
            raise serializers.ValidationError(
                "Selected section does not belong to the selected class"
            )
        
        # Check section capacity
        if section and section.is_full:
            raise serializers.ValidationError(
                f"Section {section.name} is at maximum capacity"
            )
        
        return attrs

    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'user_type': 'student'
        }
        password = validated_data.pop('password')
        
        # Create user
        user = User(**user_data)
        user.set_password(password)
        user.save()
        
        # Create student
        student = Student.objects.create(user=user, **validated_data)
        return student


class AttendanceByClassSerializer(serializers.Serializer):
    """Serializer for class-wise attendance data"""
    class_id = serializers.IntegerField()
    class_name = serializers.CharField()
    department = serializers.CharField()
    total_students = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class AttendanceBySectionSerializer(serializers.Serializer):
    """Serializer for section-wise attendance data"""
    section_id = serializers.IntegerField()
    section_name = serializers.CharField()
    class_name = serializers.CharField()
    total_students = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_students = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_sections = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    overall_attendance_percentage = serializers.FloatField()
    class_wise_data = AttendanceByClassSerializer(many=True)
    section_wise_data = AttendanceBySectionSerializer(many=True)