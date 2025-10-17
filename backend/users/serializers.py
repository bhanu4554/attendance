from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'employee_id', 'student_id', 'phone_number',
            'department', 'profile_image', 'is_active', 'password',
            'confirm_password', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match")
        
        # Validate user_type specific fields
        user_type = attrs.get('user_type')
        if user_type == 'employee' and not attrs.get('employee_id'):
            # employee_id will be auto-generated in model save method
            pass
        elif user_type == 'student' and not attrs.get('student_id'):
            # student_id will be auto-generated in model save method
            pass
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read-only, excluding sensitive data)"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'employee_id', 'student_id', 'phone_number',
            'department', 'profile_image', 'is_active', 'created_at'
        ]
        read_only_fields = fields