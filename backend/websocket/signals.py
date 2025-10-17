from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Temporarily disabled - Redis not running
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
from attendance.models import AttendanceRecord
from students.models import Student


channel_layer = get_channel_layer()


@receiver(post_save, sender=AttendanceRecord)
def attendance_record_updated(sender, instance, created, **kwargs):
    """Send real-time update when attendance is marked"""
    if channel_layer:
        # Get student information
        try:
            student = Student.objects.get(user=instance.user)
            
            # Prepare attendance data
            attendance_data = {
                'student_id': student.student_id,
                'student_name': student.full_name,
                'roll_number': student.roll_number,
                'class_id': student.class_obj.id,
                'class_name': student.class_obj.name,
                'section_id': student.section.id,
                'section_name': student.section.name,
                'status': instance.status,
                'check_in_time': instance.check_in_time.strftime('%H:%M') if instance.check_in_time else None,
                'marked_by_face_recognition': instance.marked_by_face_recognition,
                'confidence_score': instance.confidence_score,
                'date': instance.date.isoformat()
            }
            
            # Send to dashboard group
            async_to_sync(channel_layer.group_send)(
                'dashboard_updates',
                {
                    'type': 'attendance_update',
                    'data': {
                        'action': 'attendance_marked' if created else 'attendance_updated',
                        'attendance': attendance_data
                    }
                }
            )
            
            # Send to class-specific group
            async_to_sync(channel_layer.group_send)(
                f'class_{student.class_obj.id}',
                {
                    'type': 'attendance_marked',
                    'data': attendance_data
                }
            )
            
            # Send to section-specific group
            async_to_sync(channel_layer.group_send)(
                f'section_{student.section.id}',
                {
                    'type': 'attendance_marked',
                    'data': attendance_data
                }
            )
            
        except Student.DoesNotExist:
            # Handle case where user is not a student
            pass


@receiver([post_save, post_delete], sender=Student)
def student_updated(sender, instance, **kwargs):
    """Send update when student data changes"""
    if channel_layer:
        # Send dashboard update to refresh counts
        async_to_sync(channel_layer.group_send)(
            'dashboard_updates',
            {
                'type': 'dashboard_update',
                'data': {
                    'action': 'student_updated',
                    'student_id': instance.student_id if hasattr(instance, 'student_id') else None,
                    'class_id': instance.class_obj.id if hasattr(instance, 'class_obj') else None,
                    'section_id': instance.section.id if hasattr(instance, 'section') else None
                }
            }
        )