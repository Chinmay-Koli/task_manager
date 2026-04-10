# Task Manager API - Jira-like Backend

A modern, production-ready backend application for a team task management system inspired by Jira. Built with FastAPI, SQLAlchemy, and JWT authentication.

## 🎯 Overview

This API provides complete task management functionality with:
- ✅ JWT-based authentication
- ✅ User management and role-based access
- ✅ Jira-like task movement with position management
- ✅ Advanced filtering and sorting
- ✅ Team-wide and personal dashboard analytics
- ✅ Comprehensive validation and error handling

## 📋 Features

### Core Features
- **User Management**: Registration, login, user listings
- **Task Management**: Create, read, update, delete tasks with full CRUD operations
- **Task Movement**: Move tasks between status columns like Jira with automatic position management
- **Advanced Filtering**: Filter by status, assignee, creator, deadline, and more
- **Dashboard Analytics**: Personal and team-wide task statistics
- **Priority Management**: 1-5 priority levels for tasks
- **Deadline Tracking**: Due date management with overdue detection
- **Task Assignment**: Assign tasks to team members

### Task Statuses (3 Jira-compatible stages)
- `not_started` - Initial state
- `in_progress` - Currently being worked on
- `completed` - Finished tasks

### Authorization & Security
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Protected endpoints

## 🚀 Project Structure

```
task_manager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration & session
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── auth.py                 # JWT authentication utilities
│   └── routes/
│       ├── __init__.py
│       ├── user.py             # User endpoints (register, login, list)
│       ├── task.py             # Task CRUD & move endpoints
│       └── dashboard.py        # Analytics & statistics endpoints
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
└── Task_Manager_API.postman_collection.json  # Postman collection
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone Repository
```bash
git clone <repository-url>
cd task_manager
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
```

**Example .env file:**
```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Initialize Database
```bash
# Database tables are automatically created on first run
# Delete test.db to reset database
```

### 6. Run Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: **http://localhost:8000**

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
- **Endpoint**: `GET /health`
- **Response**: `{"status": "healthy"}`

---

## 🔐 Authentication

### 1. Register a New User
```bash
POST /api/users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "SecurePass123"
}
```

### 2. Login
```bash
POST /api/users/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use Token in Requests
Add to request headers:
```
Authorization: Bearer <your_token>
```

---

## 👥 User Management API

### Get All Users (for assignment dropdown)
```
GET /api/users?skip=0&limit=100

Response:
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2026-04-09T10:00:00"
  },
  ...
]
```

### Get Current User
```
GET /api/users/me
```

### Get User by ID
```
GET /api/users/{user_id}
```

---

## 📝 Task Management API

### Task Object Fields
```json
{
  "id": 1,
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 5000 chars)",
  "status": "not_started | in_progress | completed",
  "priority": "integer (1-5, higher is more important)",
  "position": "integer (order within status column)",
  "assigned_to": "integer (optional, user ID)",
  "created_by": "integer (user ID who created task)",
  "due_date": "ISO 8601 datetime (optional)",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "completed_at": "ISO 8601 datetime or null"
}
```

### Create Task
```
POST /api/tasks
Content-Type: application/json

{
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to API",
  "priority": 5,
  "due_date": "2026-04-20T18:00:00",
  "assigned_to": 2
}

Response: Task object
```

### Get All Tasks (with filtering)
```
GET /api/tasks?skip=0&limit=10&status=not_started&sort_by=created_at

Query Parameters:
- skip: integer (pagination offset, default: 0)
- limit: integer (max results, default: 10, max: 100)
- status: not_started | in_progress | completed
- assigned_to: integer (user ID, optional)
- created_by: integer (user ID, optional)
- overdue: boolean (filter overdue tasks, optional)
- sort_by: created_at | due_date | priority | position (default: created_at)

Response: Array of Task objects
```

### Get Task by ID
```
GET /api/tasks/{task_id}

Response: Task object with creator and assignee details
```

### Update Task
```
PUT /api/tasks/{task_id}
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "priority": 4,
  "due_date": "2026-04-25T18:00:00",
  "assigned_to": 3
}

Response: Updated Task object
```

### Move Task (Jira-like Functionality)
```
PATCH /api/tasks/{task_id}/move
Content-Type: application/json

{
  "new_status": "in_progress",
  "new_position": 1
}

Features:
- Move task between different status columns
- Reorder tasks within same column
- Automatic position management
- Sets completed_at timestamp when marked completed

Response: Task object
```

### Delete Task
```
DELETE /api/tasks/{task_id}

Response: 204 No Content
```

---

## 📊 Dashboard Analytics API

### Get Personal Dashboard Stats
```
GET /api/dashboard/stats

Returns: Personal statistics (total, completed, by status)
```

### Get Team Dashboard Stats
```
GET /api/dashboard/team-stats

Returns: Team-wide statistics with task breakdown by user
```

### Get Personal Dashboard Summary
```
GET /api/dashboard/summary

Returns:
{
  "user": { ... },
  "recent_tasks": [ ... ],
  "upcoming_tasks": [ ... ],  // Due within 7 days
  "overdue_tasks": [ ... ]
}
```

### Get User Workload
```
GET /api/dashboard/user/{user_id}/workload

Returns: Workload statistics for specific user
```

---

## 📊 Dashboard Analytics Metrics

Each dashboard endpoint returns:
- **total_tasks**: Count of all tasks
- **completed_tasks**: Count of completed tasks
- **not_started_tasks**: Count of not started tasks
- **in_progress_tasks**: Count of in progress tasks
- **high_priority_tasks**: Tasks with priority >= 4
- **overdue_tasks**: Tasks past due date (not completed)
- **completion_rate**: Percentage of completed tasks
- **tasks_by_user**: Breakdown of tasks by user (team-stats only)

---

## 🛠 Testing with Postman

### Import Collection
1. Open Postman
2. Click "Import"
3. Select `Task_Manager_API.postman_collection.json`
4. Collection will be imported with all endpoints

### Set Up Authentication
1. Register a user via `/api/users/register`
2. Login via `/api/users/login`
3. Copy the `access_token`
4. In Postman collection, set variable `auth_token` to your token
5. All authenticated requests will use this token

### Test Workflow
1. **Create Users**: Register 2-3 users
2. **Create Tasks**: Create tasks and assign to users
3. **Move Tasks**: Move tasks through statuses
4. **Filter Tasks**: Test various filter combinations
5. **View Analytics**: Check personal and team dashboards

---

## ⚠️ Error Handling

All errors follow standard HTTP status codes:

### Common Errors
| Status | Scenario |
|--------|----------|
| 400 | Bad request (invalid input, user doesn't exist) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (no permission to access resource) |
| 404 | Not found (task/user doesn't exist) |
| 409 | Conflict (duplicate username/email) |
| 422 | Validation error (invalid data format) |
| 500 | Server error |

### Error Response Format
```json
{
  "detail": "Error description"
}
```

---

## 🔒 Validation Rules

### User Registration
- Username: Must be unique, no spaces
- Email: Must be valid and unique
- Password: Minimum 6 characters
- Full Name: Optional

### Task Creation
- Title: Required, 1-200 characters
- Description: Optional, max 5000 characters
- Priority: 1-5 (integer)
- Due Date: Optional, ISO 8601 format
- Assigned To: Optional, user must exist

### Task Status
- Valid statuses: `not_started`, `in_progress`, `completed`
- Invalid status returns 400 error

---

## 🗄 Database

### Configuration
- **Default**: SQLite (local development)
- **Production**: PostgreSQL recommended

### Connection String
```
SQLite: sqlite:///./test.db
PostgreSQL: postgresql://user:password@localhost/task_manager
```

### Change Database
Edit `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost/task_manager
```

### Database Tables
- `users`: User accounts
- `tasks`: Task records

---

## 🔄 Workflow Example

### Complete Task Creation → Movement Flow

```bash
# 1. Register users
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "Pass123",
    "full_name": "Alice"
  }'

curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "email": "bob@example.com",
    "password": "Pass123",
    "full_name": "Bob"
  }'

# 2. Login as Alice
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "Pass123"}'

# Save token from response

# 3. Create task (assign to Bob)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build API",
    "description": "Create REST API",
    "priority": 5,
    "assigned_to": 2
  }'

# 4. Move task to in_progress
curl -X PATCH http://localhost:8000/api/tasks/1/move \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "in_progress",
    "new_position": 0
  }'

# 5. Move task to completed
curl -X PATCH http://localhost:8000/api/tasks/1/move \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "completed",
    "new_position": 0
  }'

# 6. View team stats
curl -X GET http://localhost:8000/api/dashboard/team-stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | Database connection string | sqlite:///./test.db | No |
| SECRET_KEY | JWT secret key | (dangerous default) | Yes* |
| ALGORITHM | JWT algorithm | HS256 | No |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 | No |

*Must change SECRET_KEY in production!

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'jose'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Database is locked"
**Solution**: Stop server, delete `test.db`, restart
```bash
rm test.db
uvicorn app.main:app --reload
```

### Issue: "Invalid token"
**Solution**: Get new token by logging in again

### Issue: 403 Forbidden on task update
**Solution**: Only creator or assignee can update tasks

---

## 🚀 Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Using Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📄 License

MIT License - feel free to use this project!

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss.

---

## 📞 Support

For issues and questions, please open a GitHub issue.
