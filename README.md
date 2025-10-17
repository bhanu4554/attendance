# AI-Powered Smart Attendance System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![Angular](https://img.shields.io/badge/angular-17+-red.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)

A comprehensive AI-powered attendance management system that uses face recognition technology to automatically track attendance for students and employees. The system provides real-time face recognition, attendance reporting, user management, and administrative dashboards with WebSocket-powered real-time updates.

## 🌟 Key Features

### 🤖 AI-Powered Face Recognition
- **Real-time Face Detection**: Instantly detect and recognize faces from webcam or uploaded images
- **High Accuracy**: Uses state-of-the-art face recognition algorithms with configurable confidence thresholds
- **Multiple Face Support**: Handles scenarios with multiple faces and provides clear feedback
- **Face Encoding Storage**: Secure storage of face encodings (not actual images) for privacy

### � Real-time Dashboard with WebSockets
- **Live Updates**: Real-time attendance statistics using WebSocket connections
- **Class & Section Filtering**: View live data by specific classes and sections
- **Interactive Charts**: Dynamic visualization of attendance patterns
- **Instant Notifications**: Real-time alerts for attendance events

### 🏫 Hierarchical Student Management
- **Department Organization**: Manage multiple departments (CS, EE, ME, etc.)
- **Class Management**: Organize students by academic years and programs
- **Section Management**: Handle multiple sections within classes
- **Student Profiles**: Comprehensive student information with guardian details

### �👥 Advanced User Management
- **Multi-Role Support**: Students, Employees, and Administrators with different access levels
- **User Registration**: Simple registration process with face capture
- **Profile Management**: Users can update their profiles and manage face encodings
- **Admin Dashboard**: Comprehensive user management for administrators

### 📊 Attendance Tracking
- **Automatic Attendance**: Face recognition automatically marks attendance
- **Manual Check-in**: Fallback option when face recognition is unavailable
- **Real-time Tracking**: Live attendance status and check-in/check-out times
- **Attendance Sessions**: Create and manage attendance sessions for events or classes

### 📈 Reports & Analytics
- **Detailed Reports**: Generate attendance reports by user, date range, department
- **Statistics Dashboard**: Visual analytics with charts and graphs
- **Export Options**: Export reports in various formats
- **Attendance Trends**: Track attendance patterns over time

### 🔧 Advanced Features
- **Holiday Management**: Configure holidays and non-working days
- **Department Management**: Organize users by departments
- **Notification System**: Real-time notifications for attendance events
- **Audit Logs**: Complete logging of all face recognition attempts
- **RESTful API**: Complete API for mobile app integration

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular UI    │    │  Django Backend │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│    Database     │
│  - Dashboard    │    │  - REST API     │    │                 │
│  - Face Capture │    │  - Face Recog.  │    │  - Users        │
│  - Reports      │    │  - Auth System  │    │  - Attendance   │
└─────────────────┘    └─────────────────┘    │  - Face Data    │
                                               └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │                 │
                       │  - Caching      │
                       │  - Task Queue   │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 15+
- **AI/ML**: OpenCV, face_recognition, dlib
- **Caching**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT (Simple JWT)

### Frontend
- **Framework**: Angular 17+
- **UI Library**: Bootstrap 5 + ng-bootstrap
- **Charts**: Chart.js + ng2-charts
- **Camera**: ngx-webcam
- **Icons**: Font Awesome

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (production)
- **Process Manager**: Gunicorn
- **Environment**: Python virtual environments

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd attendance-system
   ```

2. **Start with Docker Compose**
   ```bash
   # Development environment
   docker-compose up -d

   # Production environment
   docker-compose --profile production up -d
   ```

3. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000/api
   - Admin Panel: http://localhost:8000/admin

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis settings
   ```

4. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Access application**
   - Frontend: http://localhost:4200
   - Backend: http://localhost:8000

## 📖 API Documentation

### Authentication Endpoints

```http
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/refresh/
POST /api/auth/logout/
POST /api/auth/change-password/
```

### User Management

```http
GET    /api/users/              # List users
POST   /api/users/              # Create user
GET    /api/users/{id}/         # Get user details
PUT    /api/users/{id}/         # Update user
DELETE /api/users/{id}/         # Delete user
GET    /api/users/profile/      # Current user profile
GET    /api/users/stats/        # User statistics (admin)
```

### Attendance Management

```http
GET    /api/attendance/records/          # List attendance records
POST   /api/attendance/records/          # Create attendance record
GET    /api/attendance/records/{id}/     # Get attendance details
PUT    /api/attendance/records/{id}/     # Update attendance
DELETE /api/attendance/records/{id}/     # Delete attendance
GET    /api/attendance/stats/            # Attendance statistics
POST   /api/attendance/check-in/         # Manual check-in
GET    /api/attendance/report/           # Generate reports
```

### Face Recognition

```http
GET    /api/face-recognition/encodings/     # List face encodings
POST   /api/face-recognition/register/     # Register face
POST   /api/face-recognition/recognize/    # Recognize face
GET    /api/face-recognition/logs/         # Recognition logs
GET    /api/face-recognition/stats/        # Recognition statistics
DELETE /api/face-recognition/delete-encoding/{user_id}/  # Delete encoding
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=attendance_system
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL
FRONTEND_URL=http://localhost:4200
```

### Face Recognition Settings

In `backend/attendance_system/settings.py`:

```python
# Face Recognition Configuration
FACE_RECOGNITION_TOLERANCE = 0.6  # Lower = more strict
FACE_RECOGNITION_MODEL = 'hog'     # 'hog' or 'cnn'
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run e2e

# Test coverage
ng test --code-coverage
```

## 📱 Mobile App Integration

The system provides a complete REST API that can be used to build mobile applications:

### Example Mobile Integration

```javascript
// Login
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

// Face Recognition
const formData = new FormData();
formData.append('image', imageFile);
formData.append('location', 'Mobile App');

const recognitionResponse = await fetch('/api/face-recognition/recognize/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${accessToken}` },
  body: formData
});
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Permission System**: Role-based access control
- **Face Data Privacy**: Only face encodings stored, not actual images
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Secure cross-origin resource sharing
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Built-in XSS protection

## 🚀 Deployment

### Production Deployment with Docker

1. **Update environment variables**
   ```bash
   # Update docker-compose.yml for production
   # Set DEBUG=False
   # Configure proper SECRET_KEY
   # Setup SSL certificates
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose --profile production up -d
   ```

3. **Setup SSL (recommended)**
   ```bash
   # Add SSL certificates to nginx configuration
   # Update nginx.conf with SSL settings
   ```

### Traditional Deployment

1. **Server Requirements**
   - Ubuntu 20.04+ / CentOS 8+
   - Python 3.11+, Node.js 18+
   - PostgreSQL 15+, Redis 7+
   - Nginx, Supervisor

2. **Setup Steps**
   ```bash
   # Install system dependencies
   sudo apt-get update
   sudo apt-get install python3.11 python3.11-venv postgresql redis-server nginx

   # Deploy application
   git clone <repository>
   # Setup virtual environment
   # Configure databases
   # Setup Nginx and Supervisor
   ```

## 📊 Performance Optimization

- **Database Indexing**: Optimized database queries with proper indexing
- **Caching**: Redis caching for frequently accessed data
- **Image Optimization**: Efficient image processing for face recognition
- **Lazy Loading**: Frontend lazy loading for better performance
- **CDN Ready**: Static files can be served from CDN
- **Database Connection Pooling**: Efficient database connections

## 🐛 Troubleshooting

### Common Issues

1. **Face Recognition Not Working**
   ```bash
   # Check if dlib is installed correctly
   pip install dlib
   
   # For Windows, you might need:
   pip install cmake
   pip install dlib
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   
   # Check connection settings in .env
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Delete node_modules and reinstall
   rm -rf node_modules
   npm install
   ```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use Angular style guide for TypeScript
- Write tests for new features
- Update documentation
- Ensure Docker setup works

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Create an issue on GitHub for bug reports
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact the maintainers for security issues

## 🗺️ Roadmap

- [ ] Mobile application (React Native / Flutter)
- [ ] Advanced analytics dashboard
- [ ] Integration with LDAP/Active Directory
- [ ] Biometric authentication options
- [ ] Multi-campus support
- [ ] Advanced reporting with PDF generation
- [ ] Real-time notifications via WebSocket
- [ ] Integration with HR systems
- [ ] Advanced face recognition models
- [ ] Cloud deployment guides (AWS, Azure, GCP)

## 📈 Changelog

### v1.0.0 (2025-01-01)
- Initial release
- Basic face recognition functionality
- User management system
- Attendance tracking
- Admin dashboard
- Docker deployment setup

---

**Built with ❤️ using Django, Angular, and AI**