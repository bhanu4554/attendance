from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta
from .models import AttendanceRecord, AttendanceSession, Holiday
from .serializers import (
    AttendanceRecordSerializer,
    AttendanceSessionSerializer,
    HolidaySerializer,
    CheckInSerializer
)

User = get_user_model()


class AttendanceRecordListCreateView(generics.ListCreateAPIView):
    """List attendance records or create a new record"""
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AttendanceRecord.objects.all()
        
        # Filter by user if not admin
        if self.request.user.user_type != 'admin':
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by user_id if admin wants to see specific user
        user_id = self.request.query_params.get('user_id')
        if user_id and self.request.user.user_type == 'admin':
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-date', '-check_in_time')


class AttendanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an attendance record"""
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        obj = super().get_object()
        # Users can only access their own records unless they're admin
        if self.request.user.user_type != 'admin' and obj.user != self.request.user:
            self.permission_denied(self.request)
        return obj


class AttendanceSessionListCreateView(generics.ListCreateAPIView):
    """List attendance sessions or create a new session"""
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Only admins can create sessions
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(created_by=self.request.user)


class HolidayListCreateView(generics.ListCreateAPIView):
    """List holidays or create a new holiday"""
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Only admins can create holidays
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_stats(request):
    """Get attendance statistics"""
    user_id = request.query_params.get('user_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Determine which user's stats to get
    if user_id and request.user.user_type == 'admin':
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        target_user = request.user
    
    # Set default date range (current month)
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get attendance records for the period
    records = AttendanceRecord.objects.filter(
        user=target_user,
        date__range=[start_date, end_date]
    )
    
    total_days = (end_date - start_date).days + 1
    present_days = records.filter(status='present').count()
    absent_days = records.filter(status='absent').count()
    late_days = records.filter(status='late').count()
    
    # Calculate attendance percentage
    working_days = total_days - Holiday.objects.filter(
        date__range=[start_date, end_date],
        is_active=True
    ).count()
    
    attendance_percentage = (
        (present_days + late_days) / working_days * 100 
        if working_days > 0 else 0
    )
    
    # Calculate average check-in time
    check_in_records = records.filter(check_in_time__isnull=False)
    if check_in_records.exists():
        avg_check_in = check_in_records.aggregate(
            avg_time=Avg('check_in_time__time')
        )['avg_time']
    else:
        avg_check_in = None
    
    # Calculate total hours worked
    total_duration = timedelta()
    for record in records:
        if record.duration:
            total_duration += record.duration
    
    return Response({
        'user_id': target_user.id,
        'username': target_user.username,
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'total_days': total_days,
        'working_days': working_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'attendance_percentage': round(attendance_percentage, 2),
        'average_check_in_time': avg_check_in,
        'total_hours_worked': str(total_duration)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def manual_check_in(request):
    """Manual check-in for users (fallback when face recognition fails)"""
    user = request.user
    today = timezone.now().date()
    location = request.data.get('location', '')
    
    try:
        # Check if already checked in today
        attendance, created = AttendanceRecord.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'check_in_time': timezone.now(),
                'status': 'present',
                'marked_by_face_recognition': False,
                'location': location
            }
        )
        
        if created:
            return Response({
                'success': True,
                'message': 'Check-in successful',
                'action': 'check_in',
                'time': attendance.check_in_time
            }, status=status.HTTP_201_CREATED)
        elif not attendance.check_out_time:
            # Update check-out time
            attendance.check_out_time = timezone.now()
            attendance.save()
            return Response({
                'success': True,
                'message': 'Check-out successful',
                'action': 'check_out',
                'time': attendance.check_out_time
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Already checked in and out for today'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_report(request):
    """Generate attendance report"""
    if request.user.user_type != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    user_type = request.query_params.get('user_type')
    department = request.query_params.get('department')
    
    # Set default date range (current month)
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Build user queryset based on filters
    users_queryset = User.objects.filter(is_active=True)
    
    if user_type:
        users_queryset = users_queryset.filter(user_type=user_type)
    
    if department:
        users_queryset = users_queryset.filter(department=department)
    
    report_data = []
    
    for user in users_queryset:
        # Get attendance records for the period
        records = AttendanceRecord.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        present_days = records.filter(status='present').count()
        absent_days = records.filter(status='absent').count()
        late_days = records.filter(status='late').count()
        
        # Calculate working days (excluding holidays)
        total_days = (end_date - start_date).days + 1
        working_days = total_days - Holiday.objects.filter(
            date__range=[start_date, end_date],
            is_active=True
        ).count()
        
        attendance_percentage = (
            (present_days + late_days) / working_days * 100 
            if working_days > 0 else 0
        )
        
        report_data.append({
            'user_id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'email': user.email,
            'user_type': user.user_type,
            'department': user.department,
            'employee_id': user.employee_id,
            'student_id': user.student_id,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'working_days': working_days,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    return Response({
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'filters': {
            'user_type': user_type,
            'department': department
        },
        'report': report_data,
        'summary': {
            'total_users': len(report_data),
            'average_attendance': round(
                sum(item['attendance_percentage'] for item in report_data) / len(report_data)
                if report_data else 0, 2
            )
        }
    })