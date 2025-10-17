from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from .models import FaceEncoding, FaceRecognitionLog
from .serializers import (
    FaceEncodingSerializer,
    FaceRecognitionLogSerializer,
    FaceRegistrationSerializer,
    FaceRecognitionSerializer,
    FaceRecognitionResponseSerializer
)
from .services_basic import FaceRecognitionService
from attendance.models import AttendanceRecord

User = get_user_model()


class FaceEncodingListView(generics.ListAPIView):
    """List all face encodings"""
    queryset = FaceEncoding.objects.all()
    serializer_class = FaceEncodingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admin can see all, users can only see their own
        if self.request.user.user_type == 'admin':
            return FaceEncoding.objects.all().order_by('-created_at')
        return FaceEncoding.objects.filter(user=self.request.user)


class FaceRecognitionLogListView(generics.ListAPIView):
    """List face recognition logs"""
    queryset = FaceRecognitionLog.objects.all()
    serializer_class = FaceRecognitionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admin can see all, users can only see their own
        if self.request.user.user_type == 'admin':
            return FaceRecognitionLog.objects.all().order_by('-timestamp')
        return FaceRecognitionLog.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_face(request):
    """Register a user's face encoding"""
    serializer = FaceRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = serializer.validated_data['user_id']
    image = serializer.validated_data['image']
    
    # Check if user exists
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - users can only register their own face, admins can register any
    if request.user.user_type != 'admin' and user != request.user:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Initialize face recognition service
        face_service = FaceRecognitionService()
        
        # Preprocess image
        image_array = face_service.preprocess_image(image)
        
        # Register face
        success, error = face_service.register_user_face(user, image_array)
        
        if success:
            return Response({
                'success': True,
                'message': f'Face registered successfully for {user.username}'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': error
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow anonymous access for face recognition
def recognize_face(request):
    """Recognize a face and optionally mark attendance"""
    serializer = FaceRecognitionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    image = serializer.validated_data['image']
    location = serializer.validated_data.get('location', '')
    
    try:
        # Initialize face recognition service
        face_service = FaceRecognitionService()
        
        # Preprocess image
        image_array = face_service.preprocess_image(image)
        
        # Recognize face
        result = face_service.recognize_face(image_array, location)
        
        response_data = {
            'success': result['success'],
            'confidence': result.get('confidence'),
            'error': result.get('error')
        }
        
        if result['success'] and result['user']:
            user = result['user']
            
            # Add user details to response
            from users.serializers import UserProfileSerializer
            response_data['user'] = UserProfileSerializer(user).data
            
            # Optionally mark attendance
            today = timezone.now().date()
            attendance, created = AttendanceRecord.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'check_in_time': timezone.now(),
                    'status': 'present',
                    'marked_by_face_recognition': True,
                    'confidence_score': result['confidence'],
                    'location': location
                }
            )
            
            if not created and not attendance.check_out_time:
                # Update check-out time if this is a second scan
                attendance.check_out_time = timezone.now()
                attendance.save()
                response_data['action'] = 'check_out'
            else:
                response_data['action'] = 'check_in'
            
            response_data['attendance_marked'] = True
            
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recognition_stats(request):
    """Get face recognition statistics"""
    if request.user.user_type != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get statistics
    total_attempts = FaceRecognitionLog.objects.count()
    successful = FaceRecognitionLog.objects.filter(status='success').count()
    failed = FaceRecognitionLog.objects.filter(status='failed').count()
    no_face = FaceRecognitionLog.objects.filter(status='no_face').count()
    unknown_person = FaceRecognitionLog.objects.filter(status='unknown_person').count()
    
    # Calculate success rate
    success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get average processing time
    logs_with_time = FaceRecognitionLog.objects.filter(processing_time__isnull=False)
    avg_processing_time = logs_with_time.aggregate(
        avg_time=models.Avg('processing_time')
    )['avg_time'] or 0
    
    return Response({
        'total_attempts': total_attempts,
        'successful': successful,
        'failed': failed,
        'no_face_detected': no_face,
        'unknown_person': unknown_person,
        'success_rate': round(success_rate, 2),
        'average_processing_time': round(avg_processing_time, 3)
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_face_encoding(request, user_id):
    """Delete a user's face encoding"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user.user_type != 'admin' and user != request.user:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        face_encoding = FaceEncoding.objects.get(user=user)
        face_encoding.delete()
        return Response({
            'success': True,
            'message': f'Face encoding deleted for {user.username}'
        }, status=status.HTTP_200_OK)
    except FaceEncoding.DoesNotExist:
        return Response(
            {'error': 'No face encoding found for this user'}, 
            status=status.HTTP_404_NOT_FOUND
        )