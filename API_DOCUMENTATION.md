# API Documentation - AI-Powered Smart Attendance System

Comprehensive API reference for the Django REST Framework backend with WebSocket support and hierarchical student management.

## 📋 Base Information

- **Base URL**: `http://localhost:8000/api/`
- **Authentication**: JWT Bearer Token
- **Content-Type**: `application/json`
- **API Version**: v1
- **WebSocket URL**: `ws://localhost:8000/ws/`

## 🔐 Authentication

All API endpoints (except registration and login) require JWT authentication.

### Headers
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Authentication Endpoints

### Login
```http
POST /auth/login/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "employee",
    "employee_id": "EMP0001",
    "department": "IT",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Register
```http
POST /auth/register/
```

**Request Body:**
```json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "confirm_password": "secure_password",
  "first_name": "New",
  "last_name": "User",
  "user_type": "student",
  "department": "Computer Science",
  "phone_number": "+1234567890"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": 2,
  "username": "new_user"
}
```

### Refresh Token
```http
POST /auth/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## User Management

### List Users
```http
GET /users/?user_type=student&page=1
```

**Query Parameters:**
- `user_type` (optional): Filter by user type (student, employee, admin)
- `page` (optional): Page number for pagination

**Response (200):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "employee",
      "employee_id": "EMP0001",
      "department": "IT",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get User Profile
```http
GET /users/profile/
```

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "employee",
  "employee_id": "EMP0001",
  "department": "IT",
  "phone_number": "+1234567890",
  "profile_image": "/media/profiles/john_profile.jpg",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Update User Profile
```http
PUT /users/profile/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john.smith@example.com",
  "phone_number": "+1234567890",
  "department": "IT Support"
}
```

### Get User Statistics (Admin Only)
```http
GET /users/stats/
```

**Response (200):**
```json
{
  "total_users": 150,
  "students": 120,
  "employees": 25,
  "admins": 5,
  "active_users": 145,
  "inactive_users": 5
}
```

---

## Attendance Management

### List Attendance Records
```http
GET /attendance/records/?start_date=2025-01-01&end_date=2025-01-31&user_id=1
```

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `user_id` (optional): Filter by user (admin only)

**Response (200):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_details": {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "date": "2025-01-15",
      "check_in_time": "2025-01-15T09:00:00Z",
      "check_out_time": "2025-01-15T17:30:00Z",
      "status": "present",
      "marked_by_face_recognition": true,
      "confidence_score": 0.95,
      "location": "Main Office",
      "duration": "8h 30m",
      "created_at": "2025-01-15T09:00:00Z"
    }
  ]
}
```

### Manual Check-in
```http
POST /attendance/check-in/
```

**Request Body:**
```json
{
  "location": "Remote Work"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Check-in successful",
  "action": "check_in",
  "time": "2025-01-15T09:15:00Z"
}
```

### Get Attendance Statistics
```http
GET /attendance/stats/?user_id=1&start_date=2025-01-01&end_date=2025-01-31
```

**Response (200):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "total_days": 31,
  "working_days": 23,
  "present_days": 20,
  "absent_days": 2,
  "late_days": 1,
  "attendance_percentage": 91.3,
  "average_check_in_time": "09:05:00",
  "total_hours_worked": "160h 30m"
}
```

### Generate Attendance Report (Admin Only)
```http
GET /attendance/report/?start_date=2025-01-01&end_date=2025-01-31&user_type=employee
```

**Query Parameters:**
- `start_date`: Report start date
- `end_date`: Report end date
- `user_type` (optional): Filter by user type
- `department` (optional): Filter by department

**Response (200):**
```json
{
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "filters": {
    "user_type": "employee",
    "department": null
  },
  "report": [
    {
      "user_id": 1,
      "username": "john_doe",
      "full_name": "John Doe",
      "email": "john@example.com",
      "user_type": "employee",
      "department": "IT",
      "employee_id": "EMP0001",
      "present_days": 20,
      "absent_days": 2,
      "late_days": 1,
      "working_days": 23,
      "attendance_percentage": 91.3
    }
  ],
  "summary": {
    "total_users": 25,
    "average_attendance": 88.5
  }
}
```

---

## Face Recognition

### Register Face
```http
POST /face-recognition/register/
```

**Request Body (multipart/form-data):**
```
user_id: 1
image: [image file]
```

**Response (201):**
```json
{
  "success": true,
  "message": "Face registered successfully for john_doe"
}
```

### Recognize Face (Mark Attendance)
```http
POST /face-recognition/recognize/
```

**Request Body (multipart/form-data):**
```
image: [image file]
location: Main Office (optional)
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "employee"
  },
  "confidence": 0.95,
  "action": "check_in",
  "attendance_marked": true
}
```

### List Face Encodings
```http
GET /face-recognition/encodings/
```

**Response (200):**
```json
[
  {
    "id": 1,
    "user": 1,
    "user_details": {
      "id": 1,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "confidence_threshold": 0.6,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Recognition Logs (Admin Only)
```http
GET /face-recognition/logs/?status=success&page=1
```

**Query Parameters:**
- `status` (optional): Filter by status (success, failed, no_face, unknown_person)

**Response (200):**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_details": {
        "username": "john_doe"
      },
      "status": "success",
      "confidence_score": 0.95,
      "location": "Main Office",
      "timestamp": "2025-01-15T09:00:00Z",
      "processing_time": 0.234
    }
  ]
}
```

### Recognition Statistics (Admin Only)
```http
GET /face-recognition/stats/
```

**Response (200):**
```json
{
  "total_attempts": 1000,
  "successful": 920,
  "failed": 50,
  "no_face_detected": 20,
  "unknown_person": 10,
  "success_rate": 92.0,
  "average_processing_time": 0.245
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Given token not valid for any token type"
}
```

### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

### 404 Not Found
```json
{
  "error": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- Authentication endpoints: 5 requests per minute
- Face recognition: 10 requests per minute
- Other endpoints: 100 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Pagination

List endpoints use cursor-based pagination:

**Request:**
```http
GET /api/users/?page=2&page_size=10
```

**Response:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/users/?page=3",
  "previous": "http://localhost:8000/api/users/?page=1",
  "results": [...]
}
```

---

## File Uploads

Image uploads for face registration and recognition:

- **Supported formats**: JPEG, PNG, WebP
- **Maximum file size**: 10MB
- **Recommended image size**: 640x480 or higher
- **Face requirements**: Single face, clear visibility, good lighting

**Example using curl:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "user_id=1" \
  -F "image=@face_photo.jpg" \
  http://localhost:8000/api/face-recognition/register/
```