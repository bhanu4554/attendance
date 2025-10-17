from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q, Case, When, IntegerField, FloatField
from django.db.models.functions import Cast
from datetime import datetime, date
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    AcademicYear, Department, Class, Section, Student, 
    Subject, ClassSubject
)
from .serializers import (
    AcademicYearSerializer, DepartmentSerializer, ClassSerializer,
    SectionSerializer, StudentSerializer, StudentCreateSerializer,
    SubjectSerializer, ClassSubjectSerializer, AttendanceByClassSerializer,
    AttendanceBySectionSerializer, DashboardStatsSerializer
)
from attendance.models import AttendanceRecord

User = get_user_model()


class AcademicYearListCreateView(generics.ListCreateAPIView):
    """List and create academic years"""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class DepartmentListCreateView(generics.ListCreateAPIView):
    """List and create departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class ClassListCreateView(generics.ListCreateAPIView):
    """List and create classes"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'academic_year', 'grade_level', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'grade_level', 'created_at']
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class SectionListCreateView(generics.ListCreateAPIView):
    """List and create sections"""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'is_active']
    search_fields = ['name', 'room_number']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class StudentListCreateView(generics.ListCreateAPIView):
    """List and create students"""
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'section', 'gender', 'is_active']
    search_fields = ['student_id', 'roll_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['student_id', 'roll_number', 'admission_date', 'created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer
    
    def get_queryset(self):
        queryset = Student.objects.select_related(
            'user', 'class_obj', 'section', 'class_obj__department'
        ).all()
        
        # Filter by user permissions
        if self.request.user.user_type == 'employee':
            # Teachers can see students from their classes/sections
            managed_classes = Class.objects.filter(class_teacher=self.request.user)
            managed_sections = Section.objects.filter(section_teacher=self.request.user)
            queryset = queryset.filter(
                Q(class_obj__in=managed_classes) | Q(section__in=managed_sections)
            )
        elif self.request.user.user_type == 'student':
            # Students can only see their own data
            try:
                student = Student.objects.get(user=self.request.user)
                queryset = queryset.filter(id=student.id)
            except Student.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.order_by('class_obj', 'section', 'roll_number')
    
    def perform_create(self, serializer):
        if self.request.user.user_type not in ['admin', 'employee']:
            return Response(
                {'error': 'Admin or teacher access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete student"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        obj = super().get_object()
        
        # Check permissions
        if (self.request.user.user_type not in ['admin', 'employee'] and 
            obj.user != self.request.user):
            self.permission_denied(self.request)
        
        return obj


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    if request.user.user_type not in ['admin', 'employee']:
        return Response(
            {'error': 'Admin or teacher access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    today = timezone.now().date()
    
    # Basic counts
    total_students = Student.objects.filter(is_active=True).count()
    total_classes = Class.objects.filter(is_active=True).count()
    total_sections = Section.objects.filter(is_active=True).count()
    total_departments = Department.objects.filter(is_active=True).count()
    
    # Today's attendance
    today_attendance = AttendanceRecord.objects.filter(date=today)
    present_today = today_attendance.filter(status__in=['present', 'late']).count()
    absent_today = total_students - present_today
    
    overall_attendance_percentage = (present_today / total_students * 100) if total_students > 0 else 0
    
    # Class-wise attendance
    class_attendance = []
    for class_obj in Class.objects.filter(is_active=True):
        students_in_class = Student.objects.filter(class_obj=class_obj, is_active=True)
        total_class_students = students_in_class.count()
        
        if total_class_students > 0:
            present_in_class = today_attendance.filter(
                user__in=[s.user for s in students_in_class],
                status__in=['present', 'late']
            ).count()
            
            absent_in_class = total_class_students - present_in_class
            class_percentage = (present_in_class / total_class_students * 100)
            
            class_attendance.append({
                'class_id': class_obj.id,
                'class_name': class_obj.name,
                'department': class_obj.department.name,
                'total_students': total_class_students,
                'present_today': present_in_class,
                'absent_today': absent_in_class,
                'attendance_percentage': round(class_percentage, 2)
            })
    
    # Section-wise attendance
    section_attendance = []
    for section in Section.objects.filter(is_active=True):
        students_in_section = Student.objects.filter(section=section, is_active=True)
        total_section_students = students_in_section.count()
        
        if total_section_students > 0:
            present_in_section = today_attendance.filter(
                user__in=[s.user for s in students_in_section],
                status__in=['present', 'late']
            ).count()
            
            absent_in_section = total_section_students - present_in_section
            section_percentage = (present_in_section / total_section_students * 100)
            
            section_attendance.append({
                'section_id': section.id,
                'section_name': section.name,
                'class_name': section.class_obj.name,
                'total_students': total_section_students,
                'present_today': present_in_section,
                'absent_today': absent_in_section,
                'attendance_percentage': round(section_percentage, 2)
            })
    
    data = {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_sections': total_sections,
        'total_departments': total_departments,
        'present_today': present_today,
        'absent_today': absent_today,
        'overall_attendance_percentage': round(overall_attendance_percentage, 2),
        'class_wise_data': class_attendance,
        'section_wise_data': section_attendance
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_by_class(request, class_id):
    """Get detailed attendance for a specific class"""
    try:
        class_obj = Class.objects.get(id=class_id, is_active=True)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if (request.user.user_type not in ['admin'] and 
        class_obj.class_teacher != request.user):
        return Response(
            {'error': 'Access denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = start_date
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    students = Student.objects.filter(class_obj=class_obj, is_active=True)
    attendance_data = []
    
    for student in students:
        attendance_records = AttendanceRecord.objects.filter(
            user=student.user,
            date__range=[start_date, end_date]
        )
        
        present_days = attendance_records.filter(status__in=['present', 'late']).count()
        total_days = (end_date - start_date).days + 1
        percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        attendance_data.append({
            'student_id': student.student_id,
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'section': student.section.name,
            'present_days': present_days,
            'total_days': total_days,
            'attendance_percentage': round(percentage, 2),
            'recent_records': [
                {
                    'date': record.date,
                    'status': record.status,
                    'check_in_time': record.check_in_time,
                    'marked_by_face_recognition': record.marked_by_face_recognition
                }
                for record in attendance_records.order_by('-date')[:5]
            ]
        })
    
    return Response({
        'class_info': {
            'id': class_obj.id,
            'name': class_obj.name,
            'department': class_obj.department.name,
            'total_students': len(attendance_data)
        },
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'students_attendance': attendance_data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_by_section(request, section_id):
    """Get detailed attendance for a specific section"""
    try:
        section = Section.objects.get(id=section_id, is_active=True)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if (request.user.user_type not in ['admin'] and 
        section.section_teacher != request.user and
        section.class_obj.class_teacher != request.user):
        return Response(
            {'error': 'Access denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = start_date
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    students = Student.objects.filter(section=section, is_active=True)
    attendance_data = []
    
    for student in students:
        attendance_records = AttendanceRecord.objects.filter(
            user=student.user,
            date__range=[start_date, end_date]
        )
        
        present_days = attendance_records.filter(status__in=['present', 'late']).count()
        total_days = (end_date - start_date).days + 1
        percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        attendance_data.append({
            'student_id': student.student_id,
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'present_days': present_days,
            'total_days': total_days,
            'attendance_percentage': round(percentage, 2),
            'recent_records': [
                {
                    'date': record.date,
                    'status': record.status,
                    'check_in_time': record.check_in_time,
                    'marked_by_face_recognition': record.marked_by_face_recognition
                }
                for record in attendance_records.order_by('-date')[:5]
            ]
        })
    
    return Response({
        'section_info': {
            'id': section.id,
            'name': section.name,
            'class_name': section.class_obj.name,
            'department': section.class_obj.department.name,
            'total_students': len(attendance_data)
        },
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'students_attendance': attendance_data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_search(request):
    """Search students with filters"""
    if request.user.user_type not in ['admin', 'employee']:
        return Response(
            {'error': 'Admin or teacher access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    query = request.query_params.get('q', '')
    class_id = request.query_params.get('class_id')
    section_id = request.query_params.get('section_id')
    department_id = request.query_params.get('department_id')
    
    students = Student.objects.filter(is_active=True)
    
    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
    
    if class_id:
        students = students.filter(class_obj_id=class_id)
    
    if section_id:
        students = students.filter(section_id=section_id)
    
    if department_id:
        students = students.filter(class_obj__department_id=department_id)
    
    # Limit results
    students = students[:20]
    
    results = []
    for student in students:
        results.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.full_name,
            'roll_number': student.roll_number,
            'class_name': student.class_obj.name,
            'section_name': student.section.name,
            'department': student.class_obj.department.name,
            'email': student.user.email
        })
    
    return Response(results)