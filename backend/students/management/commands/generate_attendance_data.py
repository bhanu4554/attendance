from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from students.models import Student, Class, Section
from attendance.models import AttendanceRecord

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate sample attendance data for testing dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate attendance for (default: 30)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing attendance data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing attendance data...')
            AttendanceRecord.objects.all().delete()

        days = options['days']
        students = Student.objects.filter(is_active=True)
        
        if not students.exists():
            self.stdout.write(
                self.style.ERROR(
                    'No students found. Please run "create_sample_data" command first.'
                )
            )
            return

        self.stdout.write(f'Generating attendance data for {students.count()} students over {days} days...')

        attendance_created = 0
        today = timezone.now().date()
        
        for day_offset in range(days):
            attendance_date = today - timedelta(days=day_offset)
            
            # Skip weekends (assuming Saturday=5, Sunday=6)
            if attendance_date.weekday() >= 5:
                continue
                
            for student in students:
                # 85% attendance rate on average
                if random.random() < 0.85:
                    # Random check-in time between 8:00 and 9:30 AM
                    check_in_hour = random.randint(8, 9)
                    check_in_minute = random.randint(0, 59) if check_in_hour == 8 else random.randint(0, 30)
                    check_in_time = datetime.combine(
                        attendance_date, 
                        datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
                    )
                    
                    # Check-out time 6-8 hours later
                    hours_duration = random.randint(6, 8)
                    check_out_time = check_in_time + timedelta(hours=hours_duration, minutes=random.randint(0, 59))
                    
                    # Determine status based on check-in time
                    if check_in_hour < 9 or (check_in_hour == 9 and check_in_minute <= 15):
                        status = 'present'
                    elif check_in_hour == 9 and check_in_minute <= 30:
                        status = 'late'
                    else:
                        status = 'absent'
                    
                    # Create attendance record
                    attendance_record, created = AttendanceRecord.objects.get_or_create(
                        user=student.user,
                        date=attendance_date,
                        defaults={
                            'check_in_time': timezone.make_aware(check_in_time),
                            'check_out_time': timezone.make_aware(check_out_time),
                            'status': status
                        }
                    )
                    
                    if created:
                        attendance_created += 1
                else:
                    # Mark as absent
                    attendance_record, created = AttendanceRecord.objects.get_or_create(
                        user=student.user,
                        date=attendance_date,
                        defaults={
                            'status': 'absent'
                        }
                    )
                    
                    if created:
                        attendance_created += 1

        # Generate some statistics
        total_records = AttendanceRecord.objects.count()
        present_count = AttendanceRecord.objects.filter(status='present').count()
        late_count = AttendanceRecord.objects.filter(status='late').count()
        absent_count = AttendanceRecord.objects.filter(status='absent').count()
        
        attendance_rate = (present_count + late_count) / total_records * 100 if total_records > 0 else 0

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {attendance_created} attendance records\n'
                f'Statistics:\n'
                f'- Total records: {total_records}\n'
                f'- Present: {present_count} ({present_count/total_records*100:.1f}%)\n'
                f'- Late: {late_count} ({late_count/total_records*100:.1f}%)\n'
                f'- Absent: {absent_count} ({absent_count/total_records*100:.1f}%)\n'
                f'- Overall attendance rate: {attendance_rate:.1f}%'
            )
        )