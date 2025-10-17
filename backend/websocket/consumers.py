import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from students.models import Student, Class, Section
from attendance.models import AttendanceRecord

User = get_user_model()


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time dashboard updates"""
    
    async def connect(self):
        # Get user from token or session
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has permission to access dashboard
        if self.user.user_type not in ['admin', 'employee']:
            await self.close()
            return
        
        # Add user to dashboard group
        self.room_group_name = 'dashboard_updates'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.send_dashboard_update()
    
    async def disconnect(self, close_code):
        # Remove from dashboard group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'get_dashboard_data':
                await self.send_dashboard_update()
            elif message_type == 'get_class_data':
                class_id = text_data_json.get('class_id')
                await self.send_class_update(class_id)
            elif message_type == 'get_section_data':
                section_id = text_data_json.get('section_id')
                await self.send_section_update(section_id)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def send_dashboard_update(self):
        """Send dashboard statistics update"""
        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': stats
        }))
    
    async def send_class_update(self, class_id):
        """Send class-specific update"""
        if not class_id:
            return
            
        class_data = await self.get_class_attendance_data(class_id)
        await self.send(text_data=json.dumps({
            'type': 'class_update',
            'class_id': class_id,
            'data': class_data
        }))
    
    async def send_section_update(self, section_id):
        """Send section-specific update"""
        if not section_id:
            return
            
        section_data = await self.get_section_attendance_data(section_id)
        await self.send(text_data=json.dumps({
            'type': 'section_update',
            'section_id': section_id,
            'data': section_data
        }))
    
    # Group message handlers
    async def dashboard_update(self, event):
        """Handle dashboard update from group"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))
    
    async def attendance_update(self, event):
        """Handle attendance update from group"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        today = timezone.now().date()
        
        # Basic counts
        total_students = Student.objects.filter(is_active=True).count()
        total_classes = Class.objects.filter(is_active=True).count()
        total_sections = Section.objects.filter(is_active=True).count()
        
        # Today's attendance
        today_attendance = AttendanceRecord.objects.filter(date=today)
        present_today = today_attendance.filter(status__in=['present', 'late']).count()
        absent_today = total_students - present_today
        
        overall_percentage = (present_today / total_students * 100) if total_students > 0 else 0
        
        # Class-wise data
        class_data = []
        for class_obj in Class.objects.filter(is_active=True)[:10]:  # Limit for performance
            students_in_class = Student.objects.filter(class_obj=class_obj, is_active=True)
            total_class_students = students_in_class.count()
            
            if total_class_students > 0:
                present_in_class = today_attendance.filter(
                    user__in=[s.user for s in students_in_class],
                    status__in=['present', 'late']
                ).count()
                
                class_percentage = (present_in_class / total_class_students * 100)
                
                class_data.append({
                    'class_id': class_obj.id,
                    'class_name': class_obj.name,
                    'department': class_obj.department.name,
                    'total_students': total_class_students,
                    'present_today': present_in_class,
                    'attendance_percentage': round(class_percentage, 2)
                })
        
        return {
            'total_students': total_students,
            'total_classes': total_classes,
            'total_sections': total_sections,
            'present_today': present_today,
            'absent_today': absent_today,
            'overall_attendance_percentage': round(overall_percentage, 2),
            'class_wise_data': class_data,
            'timestamp': timezone.now().isoformat()
        }
    
    @database_sync_to_async
    def get_class_attendance_data(self, class_id):
        """Get class attendance data"""
        try:
            class_obj = Class.objects.get(id=class_id, is_active=True)
        except Class.DoesNotExist:
            return {'error': 'Class not found'}
        
        today = timezone.now().date()
        students = Student.objects.filter(class_obj=class_obj, is_active=True)
        
        attendance_data = []
        for student in students:
            try:
                today_record = AttendanceRecord.objects.get(
                    user=student.user, 
                    date=today
                )
                status = today_record.status
                check_in_time = today_record.check_in_time.strftime('%H:%M') if today_record.check_in_time else None
            except AttendanceRecord.DoesNotExist:
                status = 'absent'
                check_in_time = None
            
            attendance_data.append({
                'student_id': student.student_id,
                'name': student.full_name,
                'roll_number': student.roll_number,
                'section': student.section.name,
                'status': status,
                'check_in_time': check_in_time
            })
        
        return {
            'class_info': {
                'id': class_obj.id,
                'name': class_obj.name,
                'department': class_obj.department.name
            },
            'students': attendance_data,
            'timestamp': timezone.now().isoformat()
        }
    
    @database_sync_to_async
    def get_section_attendance_data(self, section_id):
        """Get section attendance data"""
        try:
            section = Section.objects.get(id=section_id, is_active=True)
        except Section.DoesNotExist:
            return {'error': 'Section not found'}
        
        today = timezone.now().date()
        students = Student.objects.filter(section=section, is_active=True)
        
        attendance_data = []
        for student in students:
            try:
                today_record = AttendanceRecord.objects.get(
                    user=student.user, 
                    date=today
                )
                status = today_record.status
                check_in_time = today_record.check_in_time.strftime('%H:%M') if today_record.check_in_time else None
            except AttendanceRecord.DoesNotExist:
                status = 'absent'
                check_in_time = None
            
            attendance_data.append({
                'student_id': student.student_id,
                'name': student.full_name,
                'roll_number': student.roll_number,
                'status': status,
                'check_in_time': check_in_time
            })
        
        return {
            'section_info': {
                'id': section.id,
                'name': section.name,
                'class_name': section.class_obj.name,
                'department': section.class_obj.department.name
            },
            'students': attendance_data,
            'timestamp': timezone.now().isoformat()
        }


class AttendanceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time attendance updates"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Add to attendance updates group
        self.room_group_name = 'attendance_updates'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'subscribe_class':
                class_id = text_data_json.get('class_id')
                await self.subscribe_to_class(class_id)
            elif message_type == 'subscribe_section':
                section_id = text_data_json.get('section_id')
                await self.subscribe_to_section(section_id)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def subscribe_to_class(self, class_id):
        """Subscribe to class-specific updates"""
        if hasattr(self, 'class_group'):
            # Leave previous class group
            await self.channel_layer.group_discard(
                self.class_group,
                self.channel_name
            )
        
        # Join new class group
        self.class_group = f'class_{class_id}'
        await self.channel_layer.group_add(
            self.class_group,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'group': 'class',
            'id': class_id
        }))
    
    async def subscribe_to_section(self, section_id):
        """Subscribe to section-specific updates"""
        if hasattr(self, 'section_group'):
            # Leave previous section group
            await self.channel_layer.group_discard(
                self.section_group,
                self.channel_name
            )
        
        # Join new section group
        self.section_group = f'section_{section_id}'
        await self.channel_layer.group_add(
            self.section_group,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'group': 'section',
            'id': section_id
        }))
    
    # Group message handlers
    async def attendance_marked(self, event):
        """Handle attendance marked event"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_marked',
            'data': event['data']
        }))
    
    async def class_update(self, event):
        """Handle class update event"""
        await self.send(text_data=json.dumps({
            'type': 'class_update',
            'data': event['data']
        }))
    
    async def section_update(self, event):
        """Handle section update event"""
        await self.send(text_data=json.dumps({
            'type': 'section_update',
            'data': event['data']
        }))