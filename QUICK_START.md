# Quick Start Guide - AI-Powered Smart Attendance System

Get the AI-Powered Smart Attendance System running in under 10 minutes!

## 🚀 One-Command Setup (Recommended)

For the fastest setup, run these commands in sequence:

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd Projcet
```

### 2. Backend Setup (Django)
```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1 djangorestframework-simplejwt==5.3.0 channels==4.0.0 channels-redis==4.1.0 django-filter==23.5

# Setup database and create sample data
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin')" | python manage.py shell
python manage.py create_sample_data --students 20
python manage.py generate_attendance_data --days 15

# Start backend server
python manage.py runserver
```

**Backend is now running on: http://localhost:8000**

### 3. Frontend Setup (Angular) - New Terminal
```bash
# Navigate to frontend (open new terminal)
cd frontend

# Install dependencies
npm install

# Start frontend server
ng serve
```

**Frontend is now running on: http://localhost:4200**

## 🎯 What You Get Immediately

### 1. Admin Access
- **URL**: http://localhost:8000/admin/
- **Username**: `admin`
- **Password**: `admin123`
- **Features**: Full Django admin interface

### 2. API Endpoints (Ready to Test)
- **Dashboard Stats**: http://localhost:8000/api/students/dashboard-stats/
- **Students List**: http://localhost:8000/api/students/students/
- **Classes**: http://localhost:8000/api/students/classes/
- **Attendance**: http://localhost:8000/api/attendance/records/

### 3. Sample Data Generated
- ✅ **5 Departments**: Computer Science, Electrical Engineering, etc.
- ✅ **20 Classes**: Year 1-4 across all departments  
- ✅ **60 Sections**: Section A, B, C for each class
- ✅ **20 Students**: With realistic data and guardian info
- ✅ **220 Attendance Records**: 15 days of attendance data (86.8% attendance rate)

### 4. Frontend Application
- **URL**: http://localhost:4200
- **Features**: Dashboard, Student Management, Real-time Updates (needs Redis)

## 🔧 Test the System

### 1. Test API with Browser
Visit these URLs in your browser:
```
http://localhost:8000/api/students/dashboard-stats/
http://localhost:8000/api/students/students/
http://localhost:8000/api/students/classes/
```

### 2. Test with curl
```bash
# Get dashboard statistics
curl http://localhost:8000/api/students/dashboard-stats/

# Get students list
curl http://localhost:8000/api/students/students/

# Get attendance by class
curl http://localhost:8000/api/students/attendance-by-class/
```

### 3. Django Admin Interface
1. Go to http://localhost:8000/admin/
2. Login with `admin` / `admin123`
3. Explore Students, Classes, Attendance Records

## 🌐 Sample API Responses

### Dashboard Statistics
```json
{
  "total_students": 20,
  "present_today": 17,
  "absent_today": 2,
  "late_today": 1,
  "attendance_rate": 90.0,
  "total_classes": 20,
  "total_sections": 60,
  "active_departments": 5
}
```

### Student List (First Student)
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "user": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "student_0001@school.edu",
        "username": "student_0001"
      },
      "roll_number": "R001",
      "class_obj": {
        "name": "Year 1",
        "department": {
          "name": "Computer Science",
          "code": "CS"
        }
      },
      "section": {
        "name": "A"
      },
      "guardian_name": "Jane Doe",
      "guardian_phone": "+1234567890",
      "is_active": true
    }
  ]
}
```

## 🎨 Next Steps

### Enable Real-time Features (Optional)
1. **Install Redis**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows (use WSL or Redis for Windows)
   ```

2. **Start Redis**:
   ```bash
   redis-server
   ```

3. **Enable WebSocket signals**:
   ```bash
   # Edit backend/websocket/apps.py
   # Change: import websocket.signals_disabled
   # To: import websocket.signals
   ```

### Add Face Recognition (Optional)
```bash
# Install dependencies (may take time)
pip install opencv-python face_recognition dlib

# Update service imports
# Edit backend/face_recognition_app/views.py
# Change: from .services_basic import FaceRecognitionService
# To: from .services import FaceRecognitionService
```

## 🐛 Quick Troubleshooting

### Backend Issues

**Django server won't start:**
```bash
# Navigate to backend directory
cd backend

# Check if you're in the right directory
ls manage.py  # Should exist

# Run from correct directory
python manage.py runserver
```

**Database errors:**
```bash
# Reset database
python manage.py flush
python manage.py migrate
python manage.py create_sample_data --students 20
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Angular server won't start:**
```bash
# Check Node.js version (need 18+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
ng serve
```

**Module not found errors:**
```bash
# Install Angular CLI globally
npm install -g @angular/cli

# Install project dependencies
npm install
```

## 📊 System Overview

You now have:
- ✅ **Django REST API** with student management
- ✅ **Real-time dashboard** capabilities (needs Redis)
- ✅ **Hierarchical student organization** (Departments → Classes → Sections → Students)
- ✅ **Attendance tracking** with statistics
- ✅ **Angular frontend** (basic setup)
- ✅ **Sample data** for testing
- ⚠️ **Face recognition** (placeholder, needs OpenCV)
- ⚠️ **WebSocket real-time** (needs Redis)

## 🚀 Development Workflow

### Making Changes

**Backend changes:**
1. Edit Python files in `backend/`
2. Django auto-reloads on file changes
3. For model changes: `python manage.py makemigrations && python manage.py migrate`

**Frontend changes:**
1. Edit TypeScript/HTML files in `frontend/src/`
2. Angular auto-reloads on file changes
3. Build for production: `ng build --prod`

### Adding New Features

**New API endpoint:**
1. Add view in appropriate `views.py`
2. Add URL in `urls.py`
3. Add serializer if needed
4. Test with browser or curl

**New frontend component:**
1. Generate: `ng generate component my-component`
2. Add to routing if needed
3. Connect to backend API

## 📚 Next Reading

- **Full Documentation**: `README.md`
- **Developer Guide**: `DEVELOPER_GUIDE.md`
- **Django Admin**: http://localhost:8000/admin/
- **API Browser**: http://localhost:8000/api/

---

**🎉 Congratulations! Your AI-Powered Smart Attendance System is running!**

The system is now ready for development and testing. Use the admin interface to explore the data, test the API endpoints, and start building additional features.