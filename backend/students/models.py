from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class AcademicYear(models.Model):
    """Model for academic years"""
    name = models.CharField(max_length=20, unique=True)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        db_table = 'academic_years'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Ensure only one active academic year
            AcademicYear.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class Department(models.Model):
    """Model for academic departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., "CS", "EE", "ME"
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'user_type__in': ['employee', 'admin']}
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        db_table = 'departments'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Class(models.Model):
    """Model for classes/grades"""
    name = models.CharField(max_length=50)  # e.g., "Class 10", "Grade A", "Year 1"
    grade_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='classes'
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='classes'
    )
    class_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_classes',
        limit_choices_to={'user_type__in': ['employee', 'admin']}
    )
    total_students = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'department', 'academic_year']
        ordering = ['department', 'grade_level', 'name']
        db_table = 'classes'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.name} - {self.department.code}"

    def update_student_count(self):
        """Update total students count"""
        self.total_students = self.students.filter(is_active=True).count()
        self.save(update_fields=['total_students'])


class Section(models.Model):
    """Model for class sections"""
    name = models.CharField(max_length=20)  # e.g., "A", "B", "Morning", "Evening"
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='sections'
    )
    section_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_sections',
        limit_choices_to={'user_type__in': ['employee', 'admin']}
    )
    max_students = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    current_students = models.IntegerField(default=0)
    room_number = models.CharField(max_length=20, blank=True)
    schedule_start_time = models.TimeField(null=True, blank=True)
    schedule_end_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'class_obj']
        ordering = ['class_obj', 'name']
        db_table = 'sections'

    def __str__(self):
        return f"{self.class_obj.name} - Section {self.name}"

    def update_student_count(self):
        """Update current students count"""
        self.current_students = self.students.filter(is_active=True).count()
        self.save(update_fields=['current_students'])

    @property
    def is_full(self):
        """Check if section is at maximum capacity"""
        return self.current_students >= self.max_students


class Student(models.Model):
    """Extended student model with academic information"""
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        limit_choices_to={'user_type': 'student'}
    )
    
    # Academic Information
    student_id = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20)
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    section = models.ForeignKey(
        Section, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    
    # Guardian Information
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)  # Father, Mother, Guardian, etc.
    
    # Academic Details
    admission_date = models.DateField()
    previous_school = models.CharField(max_length=200, blank=True)
    transport_required = models.BooleanField(default=False)
    hostel_required = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ['roll_number', 'class_obj', 'section'],
            ['student_id']
        ]
        ordering = ['class_obj', 'section', 'roll_number']
        db_table = 'students'

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # Auto-generate student_id if not provided
        if not self.student_id:
            year = self.admission_date.year
            last_student = Student.objects.filter(
                student_id__startswith=f'STU{year}'
            ).order_by('student_id').last()
            
            if last_student:
                last_number = int(last_student.student_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.student_id = f'STU{year}{str(new_number).zfill(4)}'

        super().save(*args, **kwargs)
        
        # Update section and class student counts
        if self.section:
            self.section.update_student_count()
        if self.class_obj:
            self.class_obj.update_student_count()

    def delete(self, *args, **kwargs):
        section = self.section
        class_obj = self.class_obj
        super().delete(*args, **kwargs)
        
        # Update counts after deletion
        if section:
            section.update_student_count()
        if class_obj:
            class_obj.update_student_count()

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Subject(models.Model):
    """Model for subjects"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='subjects'
    )
    credit_hours = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department', 'name']
        db_table = 'subjects'

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassSubject(models.Model):
    """Model for subjects assigned to classes"""
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='class_subjects'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='assigned_classes'
    )
    teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='teaching_subjects',
        limit_choices_to={'user_type__in': ['employee', 'admin']}
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['class_obj', 'subject']
        db_table = 'class_subjects'

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"