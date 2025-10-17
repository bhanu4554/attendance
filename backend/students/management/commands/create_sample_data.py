from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from students.models import (
    AcademicYear, Department, Class, Section, Student, 
    Subject, ClassSubject
)
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the attendance system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=100,
            help='Number of students to create (default: 100)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Student.objects.all().delete()
            ClassSubject.objects.all().delete()
            Subject.objects.all().delete()
            Section.objects.all().delete()
            Class.objects.all().delete()
            Department.objects.all().delete()
            AcademicYear.objects.all().delete()
            User.objects.filter(user_type='student').delete()

        self.stdout.write('Creating sample data...')

        # Create Academic Year
        current_year = timezone.now().year
        academic_year, created = AcademicYear.objects.get_or_create(
            name=f"{current_year}-{current_year + 1}",
            defaults={
                'start_date': date(current_year, 8, 1),
                'end_date': date(current_year + 1, 7, 31),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created academic year: {academic_year.name}')

        # Create Departments
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Electrical Engineering', 'code': 'EE'},
            {'name': 'Mechanical Engineering', 'code': 'ME'},
            {'name': 'Mathematics', 'code': 'MATH'},
            {'name': 'Physics', 'code': 'PHY'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': f"Department of {dept_data['name']}",
                    'is_active': True
                }
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'Created department: {dept.name}')

        # Create Subjects
        subjects_data = [
            {'name': 'Data Structures', 'code': 'CS101', 'department': 'CS'},
            {'name': 'Algorithms', 'code': 'CS102', 'department': 'CS'},
            {'name': 'Database Systems', 'code': 'CS201', 'department': 'CS'},
            {'name': 'Circuit Analysis', 'code': 'EE101', 'department': 'EE'},
            {'name': 'Digital Electronics', 'code': 'EE102', 'department': 'EE'},
            {'name': 'Thermodynamics', 'code': 'ME101', 'department': 'ME'},
            {'name': 'Calculus I', 'code': 'MATH101', 'department': 'MATH'},
            {'name': 'Linear Algebra', 'code': 'MATH102', 'department': 'MATH'},
            {'name': 'Quantum Physics', 'code': 'PHY201', 'department': 'PHY'},
        ]

        subjects = []
        for subj_data in subjects_data:
            dept = Department.objects.get(code=subj_data['department'])
            subj, created = Subject.objects.get_or_create(
                code=subj_data['code'],
                defaults={
                    'name': subj_data['name'],
                    'department': dept,
                    'credit_hours': random.randint(2, 4),
                    'is_active': True
                }
            )
            subjects.append(subj)
            if created:
                self.stdout.write(f'Created subject: {subj.name}')

        # Create Classes
        classes = []
        for dept in departments:
            for grade in range(1, 5):  # Grades 1-4
                class_obj, created = Class.objects.get_or_create(
                    name=f"Year {grade}",
                    department=dept,
                    academic_year=academic_year,
                    defaults={
                        'grade_level': grade,
                        'is_active': True
                    }
                )
                classes.append(class_obj)
                if created:
                    self.stdout.write(f'Created class: {class_obj.name} - {dept.code}')

        # Create Sections
        sections = []
        section_names = ['A', 'B', 'C']
        for class_obj in classes:
            for section_name in section_names:
                section, created = Section.objects.get_or_create(
                    name=section_name,
                    class_obj=class_obj,
                    defaults={
                        'max_students': random.randint(25, 35),
                        'room_number': f"{class_obj.department.code}-{class_obj.grade_level}{section_name}",
                        'schedule_start_time': f"0{random.randint(8, 9)}:00:00",
                        'schedule_end_time': f"{random.randint(15, 17)}:00:00",
                        'is_active': True
                    }
                )
                sections.append(section)
                if created:
                    self.stdout.write(f'Created section: {section}')

        # Create Students
        num_students = options['students']
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica',
            'Robert', 'Ashley', 'William', 'Amanda', 'Christopher', 'Stephanie', 'Daniel',
            'Jennifer', 'Matthew', 'Elizabeth', 'Anthony', 'Lauren', 'Mark', 'Samantha'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez'
        ]

        students_created = 0
        for i in range(num_students):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"student_{i+1:04d}"
            email = f"{username}@school.edu"
            
            # Create user
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'student',
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password('student123')
                user.save()

                # Random section
                section = random.choice(sections)
                
                # Create student profile
                student = Student.objects.create(
                    user=user,
                    roll_number=f"R{i+1:03d}",
                    class_obj=section.class_obj,
                    section=section,
                    date_of_birth=date(
                        random.randint(2000, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    gender=random.choice(['M', 'F']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    address=f"{random.randint(100, 999)} Main Street, City, State",
                    guardian_name=f"{random.choice(first_names)} {last_name}",
                    guardian_phone=f"+1{random.randint(1000000000, 9999999999)}",
                    guardian_email=f"guardian_{i+1}@email.com",
                    guardian_relation=random.choice(['Father', 'Mother', 'Guardian']),
                    admission_date=date(current_year, random.randint(1, 8), random.randint(1, 28)),
                    transport_required=random.choice([True, False]),
                    hostel_required=random.choice([True, False]),
                    is_active=True
                )
                students_created += 1

        # Create Class-Subject assignments
        for class_obj in classes:
            # Assign relevant subjects to each class
            relevant_subjects = subjects[:random.randint(3, 6)]
            for subject in relevant_subjects:
                ClassSubject.objects.get_or_create(
                    class_obj=class_obj,
                    subject=subject,
                    defaults={'is_active': True}
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(departments)} departments\n'
                f'- {len(subjects)} subjects\n'
                f'- {len(classes)} classes\n'
                f'- {len(sections)} sections\n'
                f'- {students_created} students'
            )
        )