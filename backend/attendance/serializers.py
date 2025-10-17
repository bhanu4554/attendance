from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AttendanceRecord, AttendanceSession, Holiday
from users.serializers import UserProfileSerializer

User = get_user_model()


class AttendanceRecordSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'user', 'user_details', 'date', 'check_in_time', 'check_out_time',
            'status', 'marked_by_face_recognition', 'confidence_score', 'location',
            'notes', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_details', 'duration', 'created_at', 'updated_at']
    
    def get_duration(self, obj):
        """Calculate duration between check-in and check-out"""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None
    
    def validate(self, attrs):
        """Validate attendance record data"""
        check_in = attrs.get('check_in_time')
        check_out = attrs.get('check_out_time')
        
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out time must be after check-in time"
            )
        
        return attrs


class AttendanceSessionSerializer(serializers.ModelSerializer):
    created_by_details = UserProfileSerializer(source='created_by', read_only=True)
    is_ongoing = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'name', 'description', 'start_time', 'end_time', 'is_active',
            'created_by', 'created_by_details', 'location', 'is_ongoing', 'created_at'
        ]
        read_only_fields = ['id', 'created_by_details', 'is_ongoing', 'created_at']
    
    def get_is_ongoing(self, obj):
        """Check if session is currently ongoing"""
        return obj.is_ongoing
    
    def validate(self, attrs):
        """Validate session data"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                "End time must be after start time"
            )
        
        return attrs


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'description', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_date(self, value):
        """Validate holiday date"""
        from django.utils import timezone
        
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Holiday date cannot be in the past"
            )
        
        return value


class CheckInSerializer(serializers.Serializer):
    """Serializer for manual check-in"""
    location = serializers.CharField(max_length=200, required=False, default='')

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'user', 'user_details', 'date', 'check_in_time', 'check_out_time',
            'status', 'marked_by_face_recognition', 'confidence_score', 'location',
            'notes', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_details', 'duration']

    def validate(self, attrs):
        check_in = attrs.get('check_in_time')
        check_out = attrs.get('check_out_time')
        
        if check_out and check_in and check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out time must be after check-in time"
            )
        
        return attrs


class AttendanceSessionSerializer(serializers.ModelSerializer):
    created_by_details = UserProfileSerializer(source='created_by', read_only=True)
    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'name', 'description', 'start_time', 'end_time', 'is_active',
            'created_by', 'created_by_details', 'location', 'is_ongoing',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_details', 'is_ongoing']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if end_time <= start_time:
            raise serializers.ValidationError(
                "End time must be after start time"
            )
        
        return attrs


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'date', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    average_check_in_time = serializers.TimeField()
    total_hours = serializers.DurationField()


class CheckInSerializer(serializers.Serializer):
    """Serializer for face recognition check-in"""
    image = serializers.ImageField()
    location = serializers.CharField(max_length=200, required=False)
    session_id = serializers.IntegerField(required=False)