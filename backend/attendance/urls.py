from django.urls import path
from .views import (
    AttendanceRecordListCreateView,
    AttendanceRecordDetailView,
    AttendanceSessionListCreateView,
    HolidayListCreateView,
    attendance_stats,
    manual_check_in,
    attendance_report
)

urlpatterns = [
    path('records/', AttendanceRecordListCreateView.as_view(), name='attendance-records'),
    path('records/<int:pk>/', AttendanceRecordDetailView.as_view(), name='attendance-record-detail'),
    path('sessions/', AttendanceSessionListCreateView.as_view(), name='attendance-sessions'),
    path('holidays/', HolidayListCreateView.as_view(), name='holidays'),
    path('stats/', attendance_stats, name='attendance-stats'),
    path('check-in/', manual_check_in, name='manual-check-in'),
    path('report/', attendance_report, name='attendance-report'),
]