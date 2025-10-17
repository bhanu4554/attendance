from django.urls import path
from .views import (
    AcademicYearListCreateView,
    DepartmentListCreateView,
    ClassListCreateView,
    SectionListCreateView,
    StudentListCreateView,
    StudentDetailView,
    dashboard_stats,
    attendance_by_class,
    attendance_by_section,
    student_search
)

urlpatterns = [
    # Academic Year
    path('academic-years/', AcademicYearListCreateView.as_view(), name='academic-years'),
    
    # Departments
    path('departments/', DepartmentListCreateView.as_view(), name='departments'),
    
    # Classes
    path('classes/', ClassListCreateView.as_view(), name='classes'),
    
    # Sections
    path('sections/', SectionListCreateView.as_view(), name='sections'),
    
    # Students
    path('students/', StudentListCreateView.as_view(), name='students'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/search/', student_search, name='student-search'),
    
    # Dashboard and Reports
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('attendance/class/<int:class_id>/', attendance_by_class, name='attendance-by-class'),
    path('attendance/section/<int:section_id>/', attendance_by_section, name='attendance-by-section'),
]