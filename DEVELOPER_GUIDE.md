# Developer Guide - AI-Powered Smart Attendance System

This comprehensive guide will help developers set up, understand, and contribute to the AI-Powered Smart Attendance System.

## 📋 Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [WebSocket Implementation](#websocket-implementation)
8. [Face Recognition Integration](#face-recognition-integration)
9. [Testing Guide](#testing-guide)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)

## 🛠️ Development Environment Setup

### Prerequisites Installation

#### Python Environment
```bash
# Python 3.8+ required
python --version

# Create virtual environment
python -m venv attendance_env

# Activate virtual environment
# Windows:
attendance_env\Scripts\activate
# macOS/Linux:
source attendance_env/bin/activate
```

#### Node.js Environment
```bash
# Node.js 18+ required
node --version
npm --version

# Install Angular CLI globally
npm install -g @angular/cli
```

#### Redis Server (for WebSockets)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# macOS
brew install redis

# Windows (use WSL or download Redis for Windows)
# Download from: https://redis.io/download
```

### Step-by-Step Setup

#### 1. Clone and Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd Projcet

# Create necessary directories
mkdir logs
mkdir media/face_images
```

#### 2. Backend Setup (Django)
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your configurations
SECRET_KEY=your-super-secret-key-here
DEBUG=True
DB_NAME=attendance_system
REDIS_URL=redis://localhost:6379
```

#### 3. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Generate sample data for development
python manage.py create_sample_data --students 50
python manage.py generate_attendance_data --days 30
```

#### 4. Frontend Setup (Angular)
```bash
cd ../frontend

# Install dependencies
npm install

# Create environment files
cp src/environments/environment.example.ts src/environments/environment.ts
cp src/environments/environment.example.ts src/environments/environment.prod.ts
```

#### 5. Start Development Servers

Terminal 1 - Backend:
```bash
cd backend
python manage.py runserver
# Server runs on http://localhost:8000
```

Terminal 2 - Frontend:
```bash
cd frontend
ng serve
# Application runs on http://localhost:4200
```

Terminal 3 - Redis (for WebSockets):
```bash
redis-server
# Redis runs on localhost:6379
```

## 🏗️ Project Architecture

### System Overview
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Angular Frontend  │    │   Django Backend    │    │     Database        │
│                     │    │                     │    │                     │
│ • Dashboard         │◄──►│ • REST API          │◄──►│ • PostgreSQL/SQLite │
│ • Student Mgmt      │    │ • WebSocket API     │    │ • Redis (Cache)     │
│ • Face Recognition  │    │ • Face Recognition  │    │                     │
│ • Real-time Updates │    │ • Authentication    │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Backend Architecture (Django)

```
backend/
├── attendance_system/          # Main Django project
│   ├── settings.py            # Configuration
│   ├── urls.py               # URL routing
│   ├── asgi.py               # ASGI config (WebSockets)
│   └── wsgi.py               # WSGI config
├── users/                     # User management
│   ├── models.py             # Custom User model
│   ├── views.py              # User CRUD operations
│   ├── serializers.py        # DRF serializers
│   └── urls.py               # User endpoints
├── students/                  # Student management (NEW)
│   ├── models.py             # Student hierarchy models
│   ├── views.py              # Student CRUD & statistics
│   ├── serializers.py        # Student serializers
│   ├── urls.py               # Student endpoints
│   └── management/commands/   # Data generation commands
├── attendance/               # Attendance tracking
│   ├── models.py             # Attendance records
│   ├── views.py              # Attendance operations
│   └── serializers.py        # Attendance serializers
├── face_recognition_app/     # AI face recognition
│   ├── models.py             # Face encodings
│   ├── services.py           # Face recognition logic
│   └── views.py              # Face endpoints
├── authentication/           # JWT authentication
│   ├── views.py              # Login/logout
│   └── serializers.py        # Auth serializers
└── websocket/               # Real-time features (NEW)
    ├── consumers.py          # WebSocket consumers
    ├── routing.py            # WebSocket routing
    └── signals.py            # Real-time signals
```

### Frontend Architecture (Angular)

```
frontend/src/app/
├── core/                     # Core functionality
│   ├── services/            # API services
│   ├── guards/              # Route guards
│   └── interceptors/        # HTTP interceptors
├── components/              # Feature components
│   ├── dashboard/           # Real-time dashboard
│   ├── student-management/  # Student CRUD
│   ├── attendance/          # Attendance tracking
│   └── face-recognition/    # Face capture/recognition
├── services/               # Application services
│   ├── websocket.service.ts # WebSocket client
│   ├── api.service.ts       # HTTP API client
│   └── auth.service.ts      # Authentication
└── shared/                 # Shared components
    ├── components/         # Reusable components
    └── models/            # TypeScript interfaces
```

## 🔧 Backend Development

### Model Relationships

The system uses a hierarchical structure for student organization:

```python
# students/models.py
AcademicYear (2025-2026)
    ↓
Department (Computer Science, Electrical Engineering, etc.)
    ↓
Class (Year 1, Year 2, etc.)
    ↓
Section (Section A, Section B, etc.)
    ↓
Student (Individual students)
```

### Key Models

#### Student Model
```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE)
    section = models.ForeignKey('Section', on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    # ... additional fields
```

#### Attendance Model
```python
class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by_face_recognition = models.BooleanField(default=False)
```

### API Views Pattern

#### Generic CRUD Pattern
```python
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['class_obj', 'section', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'roll_number']
    permission_classes = [IsAuthenticated]
```

#### Statistics Views
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    today = timezone.now().date()
    
    total_students = Student.objects.filter(is_active=True).count()
    present_today = AttendanceRecord.objects.filter(
        date=today, 
        status__in=['present', 'late']
    ).count()
    
    return Response({
        'total_students': total_students,
        'present_today': present_today,
        'attendance_rate': (present_today / total_students * 100) if total_students > 0 else 0
    })
```

### WebSocket Implementation

#### Consumer Classes
```python
# websocket/consumers.py
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard_updates", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'get_dashboard_stats':
            await self.send_dashboard_stats()

    async def send_dashboard_stats(self):
        # Get real-time statistics
        stats = await self.get_dashboard_statistics()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_stats',
            'data': stats
        }))
```

#### Signal Integration for Real-time Updates
```python
# websocket/signals.py
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=AttendanceRecord)
def attendance_record_saved(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'dashboard_updates',
            {
                'type': 'attendance_update',
                'data': {
                    'student_name': f"{instance.user.first_name} {instance.user.last_name}",
                    'status': instance.status,
                    'timestamp': instance.check_in_time.isoformat() if instance.check_in_time else None
                }
            }
        )
```

## 🎨 Frontend Development

### Service Architecture

#### WebSocket Service
```typescript
// services/websocket.service.ts
@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private dashboardStatsSubject = new BehaviorSubject<DashboardStats | null>(null);
  
  public dashboardStats$ = this.dashboardStatsSubject.asObservable();

  connect(): void {
    this.socket = new WebSocket('ws://localhost:8000/ws/dashboard/');
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
  }

  requestDashboardStats(): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'get_dashboard_stats'
      }));
    }
  }
}
```

#### API Service
```typescript
// services/api.service.ts
@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // Student management
  getStudents(params?: any): Observable<Student[]> {
    return this.http.get<Student[]>(`${this.baseUrl}/students/students/`, { params });
  }

  createStudent(student: any): Observable<Student> {
    return this.http.post<Student>(`${this.baseUrl}/students/students/`, student);
  }

  // Dashboard statistics
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/students/dashboard-stats/`);
  }
}
```

### Component Patterns

#### Real-time Dashboard Component
```typescript
@Component({
  selector: 'app-dashboard',
  template: `
    <div class="dashboard-stats">
      <div class="stat-card" *ngFor="let stat of stats">
        <h3>{{ stat.value }}</h3>
        <p>{{ stat.label }}</p>
      </div>
    </div>
    
    <div class="real-time-updates">
      <div *ngFor="let update of realtimeUpdates" class="update-item">
        {{ update.message }}
      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit, OnDestroy {
  stats: any[] = [];
  realtimeUpdates: any[] = [];
  private subscriptions: Subscription[] = [];

  constructor(
    private webSocketService: WebSocketService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    // Subscribe to WebSocket updates
    this.subscriptions.push(
      this.webSocketService.dashboardStats$.subscribe(stats => {
        if (stats) {
          this.updateStats(stats);
        }
      })
    );

    // Connect to WebSocket
    this.webSocketService.connect();
    this.webSocketService.requestDashboardStats();
  }
}
```

## 🗄️ Database Schema

### Core Tables

#### Users and Authentication
```sql
-- Custom User Model
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    user_type VARCHAR(20) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW()
);
```

#### Student Hierarchy
```sql
-- Academic Years
CREATE TABLE academic_years (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Classes
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    academic_year_id INTEGER REFERENCES academic_years(id),
    grade_level INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

-- Sections
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    class_id INTEGER REFERENCES classes(id),
    max_students INTEGER DEFAULT 30,
    room_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE
);

-- Students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    class_id INTEGER REFERENCES classes(id),
    section_id INTEGER REFERENCES sections(id),
    date_of_birth DATE,
    gender CHAR(1),
    guardian_name VARCHAR(100),
    guardian_phone VARCHAR(15),
    admission_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Attendance Tracking
```sql
-- Attendance Records
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE DEFAULT CURRENT_DATE,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    status VARCHAR(10) DEFAULT 'absent',
    marked_by_face_recognition BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT,
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

#### Face Recognition
```sql
-- Face Encodings
CREATE TABLE face_encodings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    encoding BYTEA NOT NULL,
    image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

### Database Indexes for Performance
```sql
-- Indexes for better query performance
CREATE INDEX idx_attendance_user_date ON attendance_records(user_id, date);
CREATE INDEX idx_attendance_date ON attendance_records(date);
CREATE INDEX idx_students_class_section ON students(class_id, section_id);
CREATE INDEX idx_face_encodings_user ON face_encodings(user_id, is_active);
```

## 🔌 API Reference

### Authentication APIs

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "user_type": "admin"
  }
}
```

### Student Management APIs

#### Dashboard Statistics
```http
GET /api/students/dashboard-stats/
Authorization: Bearer <access_token>

Response:
{
  "total_students": 50,
  "present_today": 42,
  "absent_today": 5,
  "late_today": 3,
  "attendance_rate": 90.0,
  "total_classes": 20,
  "total_sections": 60,
  "active_departments": 5
}
```

#### Student List with Filtering
```http
GET /api/students/students/?class_obj=1&section=2&search=john
Authorization: Bearer <access_token>

Response:
{
  "count": 25,
  "next": "http://localhost:8000/api/students/students/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 10,
        "username": "student_001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@school.edu"
      },
      "roll_number": "R001",
      "class_obj": {
        "id": 1,
        "name": "Year 1",
        "department": {
          "name": "Computer Science",
          "code": "CS"
        }
      },
      "section": {
        "id": 1,
        "name": "A"
      },
      "date_of_birth": "2005-01-15",
      "gender": "M",
      "guardian_name": "Jane Doe",
      "guardian_phone": "+1234567890",
      "is_active": true
    }
  ]
}
```

#### Create Student
```http
POST /api/students/students/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice.smith@school.edu",
  "username": "alice_smith",
  "roll_number": "R051",
  "class_obj": 1,
  "section": 1,
  "date_of_birth": "2005-03-20",
  "gender": "F",
  "guardian_name": "Bob Smith",
  "guardian_phone": "+1987654321",
  "guardian_email": "bob.smith@email.com"
}
```

### Attendance APIs

#### Attendance by Class
```http
GET /api/students/attendance-by-class/?date=2025-10-17
Authorization: Bearer <access_token>

Response:
[
  {
    "class_id": 1,
    "class_name": "Year 1 - CS",
    "department": "Computer Science",
    "total_students": 25,
    "present": 22,
    "absent": 2,
    "late": 1,
    "attendance_rate": 92.0
  }
]
```

### Face Recognition APIs

#### Register Face
```http
POST /api/face-recognition/register/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "user_id": 10,
  "image": <file>
}

Response:
{
  "success": true,
  "message": "Face registered successfully",
  "face_id": 1
}
```

#### Recognize Face
```http
POST /api/face-recognition/recognize/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "image": <file>
}

Response:
{
  "success": true,
  "recognized_users": [
    {
      "user_id": 10,
      "name": "John Doe",
      "confidence": 0.95,
      "roll_number": "R001"
    }
  ]
}
```

## 🚀 WebSocket Implementation

### WebSocket URLs
```python
# websocket/routing.py
websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
    re_path(r'ws/attendance/$', AttendanceConsumer.as_asgi()),
    re_path(r'ws/class/(?P<class_id>\w+)/$', ClassConsumer.as_asgi()),
]
```

### Frontend WebSocket Usage
```typescript
// Connect to dashboard updates
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');

ws.onopen = () => {
  console.log('Connected to dashboard WebSocket');
  
  // Request initial stats
  ws.send(JSON.stringify({
    type: 'get_dashboard_stats'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'dashboard_stats':
      updateDashboardStats(data.data);
      break;
    case 'attendance_update':
      showAttendanceNotification(data.data);
      break;
  }
};
```

## 🧪 Testing Guide

### Backend Testing

#### Unit Tests
```python
# students/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from students.models import Student, Department, Class, Section

User = get_user_model()

class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_student_creation(self):
        student = Student.objects.create(
            user=self.user,
            roll_number='R001',
            class_obj=self.test_class,
            section=self.test_section
        )
        self.assertEqual(student.roll_number, 'R001')
        self.assertTrue(student.is_active)
```

#### API Tests
```python
# students/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

class StudentAPITest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username='admin',
            password='admin123',
            user_type='admin'
        )
        self.client.force_authenticate(user=self.admin_user)
        
    def test_dashboard_stats(self):
        response = self.client.get('/api/students/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
```

#### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Testing

#### Unit Tests
```typescript
// dashboard.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardComponent } from './dashboard.component';
import { WebSocketService } from '../../services/websocket.service';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let mockWebSocketService: jasmine.SpyObj<WebSocketService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('WebSocketService', ['connect', 'requestDashboardStats']);

    await TestBed.configureTestingModule({
      declarations: [DashboardComponent],
      providers: [
        { provide: WebSocketService, useValue: spy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    mockWebSocketService = TestBed.inject(WebSocketService) as jasmine.SpyObj<WebSocketService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should connect to WebSocket on init', () => {
    component.ngOnInit();
    expect(mockWebSocketService.connect).toHaveBeenCalled();
  });
});
```

#### Run Frontend Tests
```bash
# Run unit tests
ng test

# Run e2e tests
ng e2e

# Run with coverage
ng test --code-coverage
```

## 🚢 Deployment Guide

### Production Environment Setup

#### 1. Environment Configuration
```bash
# .env.production
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=attendance_production
DB_USER=attendance_user
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

#### 2. PostgreSQL Setup
```sql
-- Create production database
CREATE DATABASE attendance_production;
CREATE USER attendance_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE attendance_production TO attendance_user;
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/attendance-system
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Frontend static files
    location / {
        root /var/www/attendance-frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket connections
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Static files
    location /static/ {
        alias /var/www/attendance-backend/static/;
    }
    
    location /media/ {
        alias /var/www/attendance-backend/media/;
    }
}
```

#### 4. Systemd Service
```ini
# /etc/systemd/system/attendance-backend.service
[Unit]
Description=Attendance System Django Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/attendance-backend
Environment=PATH=/var/www/attendance-backend/venv/bin
EnvironmentFile=/var/www/attendance-backend/.env
ExecStart=/var/www/attendance-backend/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### 5. Docker Production Setup
```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    cmake \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "attendance_system.wsgi:application"]
```

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: attendance_production
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://attendance_user:secure-password@db:5432/attendance_production
      - REDIS_URL=redis://redis:6379

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U attendance_user -d attendance_production

# Reset database
python manage.py flush
python manage.py migrate
```

#### 2. Redis Connection Issues
```bash
# Check Redis status
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Restart Redis
sudo systemctl restart redis-server
```

#### 3. WebSocket Connection Issues
```bash
# Check if WebSocket URL is correct
# Frontend: ws://localhost:8000/ws/dashboard/
# Production: wss://yourdomain.com/ws/dashboard/

# Verify ASGI configuration
python manage.py runserver --asgi

# Check CORS settings for WebSocket
CORS_ALLOW_ALL_ORIGINS = True  # Development only
```

#### 4. Face Recognition Library Issues
```bash
# Install system dependencies (Ubuntu)
sudo apt-get install cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

# Reinstall face_recognition
pip uninstall face_recognition dlib
pip install --no-cache-dir dlib
pip install --no-cache-dir face_recognition

# For Windows, use pre-compiled wheels
pip install https://github.com/ageitgey/face_recognition_models/releases/download/v0.3.0/face_recognition_models-0.3.0-py2.py3-none-any.whl
```

#### 5. Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version compatibility
node --version  # Should be 18+

# Build with verbose logging
ng build --verbose

# Check for TypeScript errors
ng build --watch
```

#### 6. Permission Issues
```bash
# Fix media directory permissions
sudo chown -R www-data:www-data /var/www/attendance-backend/media/
sudo chmod -R 755 /var/www/attendance-backend/media/

# Fix static files permissions
sudo chown -R www-data:www-data /var/www/attendance-backend/static/
```

### Performance Optimization

#### Database Optimization
```python
# Add database indexes
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY idx_attendance_user_date ON attendance_records(user_id, date);"
        ),
    ]

# Use select_related and prefetch_related
students = Student.objects.select_related('user', 'class_obj', 'section').prefetch_related('class_obj__department')
```

#### Frontend Optimization
```typescript
// Use OnPush change detection
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})

// Implement trackBy functions
trackByStudentId(index: number, student: Student): number {
  return student.id;
}

// Use lazy loading for routes
const routes: Routes = [
  {
    path: 'students',
    loadChildren: () => import('./students/students.module').then(m => m.StudentsModule)
  }
];
```

### Monitoring and Logging

#### Application Monitoring
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/attendance/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Performance Monitoring
```bash
# Install monitoring tools
pip install django-debug-toolbar
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

This developer guide provides comprehensive instructions for setting up, developing, and deploying the AI-Powered Smart Attendance System. Follow the sections relevant to your development needs and refer to the troubleshooting section for common issues.