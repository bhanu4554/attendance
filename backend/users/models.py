from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        null=True,
        blank=True
    )
    department = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    class Meta:
        db_table = 'users'
        
    def save(self, *args, **kwargs):
        # Ensure employee_id or student_id is set based on user_type
        if self.user_type == 'employee' and not self.employee_id:
            # Generate employee ID if not provided
            last_employee = User.objects.filter(user_type='employee').order_by('id').last()
            if last_employee and last_employee.employee_id:
                last_id = int(last_employee.employee_id.split('EMP')[-1])
                self.employee_id = f'EMP{str(last_id + 1).zfill(4)}'
            else:
                self.employee_id = 'EMP0001'
        elif self.user_type == 'student' and not self.student_id:
            # Generate student ID if not provided
            last_student = User.objects.filter(user_type='student').order_by('id').last()
            if last_student and last_student.student_id:
                last_id = int(last_student.student_id.split('STU')[-1])
                self.student_id = f'STU{str(last_id + 1).zfill(4)}'
            else:
                self.student_id = 'STU0001'
        super().save(*args, **kwargs)