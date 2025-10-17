from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    """Create student profile when a student user is created"""
    if instance.user_type == 'student' and created:
        # Student profile should be created manually by admin
        # This is just a placeholder for any additional logic
        pass


@receiver(post_save, sender=Student)
def update_section_counts(sender, instance, created, **kwargs):
    """Update section and class counts when student is created/updated"""
    if instance.section:
        instance.section.update_student_count()
    if instance.class_obj:
        instance.class_obj.update_student_count()


@receiver(post_delete, sender=Student)
def update_counts_on_delete(sender, instance, **kwargs):
    """Update counts when student is deleted"""
    if instance.section:
        instance.section.update_student_count()
    if instance.class_obj:
        instance.class_obj.update_student_count()