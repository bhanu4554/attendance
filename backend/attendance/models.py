from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_by_face_recognition = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', '-check_in_time']
        db_table = 'attendance_records'

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.status})"

    @property
    def duration(self):
        """Calculate duration between check-in and check-out"""
        if self.check_in_time and self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None

    def save(self, *args, **kwargs):
        # Auto-determine status based on check-in time
        if self.check_in_time and not self.status:
            # Define standard work hours (you can adjust these)
            standard_start_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
            if self.check_in_time <= standard_start_time:
                self.status = 'present'
            else:
                self.status = 'late'
        super().save(*args, **kwargs)


class AttendanceSession(models.Model):
    """Model to track active attendance sessions"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        db_table = 'attendance_sessions'

    def __str__(self):
        return f"{self.name} - {self.start_time.date()}"

    @property
    def is_ongoing(self):
        """Check if session is currently ongoing"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.is_active


class Holiday(models.Model):
    """Model to track holidays and non-working days"""
    name = models.CharField(max_length=200)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        db_table = 'holidays'

    def __str__(self):
        return f"{self.name} - {self.date}"