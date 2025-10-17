# Development Setup Instructions

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

## Backend Development Setup

### 1. Clone and Setup Repository
```bash
git clone <repository-url>
cd attendance-system/backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```env
SECRET_KEY=your-development-secret-key
DEBUG=True
DB_NAME=attendance_system_dev
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
```

### 5. Setup Database
```bash
# Create database
createdb attendance_system_dev

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 6. Start Development Server
```bash
python manage.py runserver
```

### 7. Start Celery Worker (Optional)
```bash
# In a new terminal
celery -A attendance_system worker --loglevel=info
```

## Frontend Development Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000/api
- Admin Interface: http://localhost:8000/admin

## Development Tools

### Code Quality
```bash
# Backend
flake8 .
black .
isort .

# Frontend
ng lint
npm run format
```

### Testing
```bash
# Backend tests
python manage.py test
coverage run --source='.' manage.py test
coverage report

# Frontend tests
ng test
ng e2e
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush

# Backup database
pg_dump attendance_system_dev > backup.sql
```

## Debugging

### Backend Debugging
- Use Django Debug Toolbar for SQL query analysis
- Enable Django logging in settings.py
- Use `pdb` or VS Code debugger

### Frontend Debugging
- Use Angular DevTools browser extension
- Enable Angular CLI analytics: `ng analytics on`
- Use browser developer tools

## Development Workflow

1. Create feature branch: `git checkout -b feature/feature-name`
2. Make changes and test locally
3. Run code quality checks
4. Write/update tests
5. Commit changes: `git commit -m "feat: add new feature"`
6. Push branch: `git push origin feature/feature-name`
7. Create pull request

## Common Development Issues

### Face Recognition Issues
```bash
# Install dlib dependencies (Ubuntu/Debian)
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev

# Windows: Use pre-compiled wheel
pip install dlib-19.24.2-cp311-cp311-win_amd64.whl
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset PostgreSQL password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'newpassword';"
```

### Node Modules Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```