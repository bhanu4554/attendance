# WebSocket signals - temporarily disabled until Redis is configured
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from attendance.models import AttendanceRecord
from students.models import Student

User = get_user_model()


@receiver(post_save, sender=AttendanceRecord)
def attendance_record_saved(sender, instance, created, **kwargs):
    """Signal handler for when attendance record is saved"""
    # TODO: Enable when Redis is configured
    pass


@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    """Signal handler for when user is saved"""
    # TODO: Enable when Redis is configured
    pass


@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    """Signal handler for when user is deleted"""
    # TODO: Enable when Redis is configured
    pass


@receiver(post_save, sender=Student)
def student_updated(sender, instance, created, **kwargs):
    """Signal handler for when student is saved"""
    # TODO: Enable when Redis is configured
    pass