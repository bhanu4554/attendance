from rest_framework import serializers
from .models import FaceEncoding, FaceRecognitionLog
from users.serializers import UserProfileSerializer


class FaceEncodingSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = FaceEncoding
        fields = [
            'id', 'user', 'user_details', 'confidence_threshold',
            'image_path', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_details']


class FaceRecognitionLogSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = FaceRecognitionLog
        fields = [
            'id', 'user', 'user_details', 'status', 'confidence_score',
            'image_path', 'location', 'timestamp', 'error_message', 'processing_time'
        ]
        read_only_fields = ['id', 'timestamp', 'user_details']


class FaceRegistrationSerializer(serializers.Serializer):
    """Serializer for face registration"""
    user_id = serializers.IntegerField()
    image = serializers.ImageField()


class FaceRecognitionSerializer(serializers.Serializer):
    """Serializer for face recognition request"""
    image = serializers.ImageField()
    location = serializers.CharField(max_length=200, required=False)


class FaceRecognitionResponseSerializer(serializers.Serializer):
    """Serializer for face recognition response"""
    success = serializers.BooleanField()
    user = UserProfileSerializer(required=False)
    confidence = serializers.FloatField(required=False)
    error = serializers.CharField(required=False)