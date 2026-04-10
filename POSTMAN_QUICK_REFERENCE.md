# Postman Collection - Quick Reference Card

## 📌 TL;DR (Too Long; Didn't Read)

### Step 1: Import Collection
```
Postman → Import → Upload Files → Task_Manager_API.postman_collection.json
```

### Step 2: Login & Get Token
1. Go to **Authentication** → **Login User**
2. Edit body with your credentials
3. Click **Send**
4. Copy the `access_token` from response

### Step 3: Set Token for All Requests
1. Collection name → **Variables** tab
2. Find `auth_token`
3. Paste token in **Current Value**
4. Click **Save**

### Step 4: Make Requests
All endpoints now have authentication! Just select endpoint and click **Send**

---

## 📚 Collection Structure

| Folder | Endpoints | Purpose |
|--------|-----------|---------|
| **Authentication** | 3 | Register, Login, Get Me |
| **User Management** | 2 | List users, Get user by ID |
| **Task Management** | 6 | CRUD operations + Move task |
| **Dashboard Analytics** | 4 | Stats, Team stats, Summary, Workload |
| **System** | 2 | Health check, Root |

---

## 🔐 Authentication Setup

### Option A: Manual (Every Time)
```
Request → Headers tab → Add:
Key: Authorization
Value: Bearer <your_token_here>
```

### Option B: Automatic (Recommended)
```
1. Login User → Get token
2. Set token in Variables
3. Test any protected endpoint
```

---

## 🎯 Common Workflows

### Create a Complete Task Workflow

**Step 1**: Register User
```json
POST /api/users/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "SecurePass123"
}
```

**Step 2**: Login
```json
POST /api/users/login
{
  "username": "john_doe",
  "password": "SecurePass123"
}
✅ Copy token → Set in variables
```

**Step 3**: Create Task
```json
POST /api/tasks
{
  "title": "My Task",
  "description": "Task details",
  "priority": 3,
  "assigned_to": 1
}
✅ Copy task ID from response
```

**Step 4**: Move Task (Jira-like)
```json
PATCH /api/tasks/{task_id}/move
{
  "new_status": "in_progress",
  "new_position": 0
}
✅ Task moved between columns
```

**Step 5**: Check Dashboard
```
GET /api/dashboard/stats
✅ See updated statistics
```

---

## 🔍 Using Query Parameters

### All Tasks with Filters
```
GET /api/tasks?status=not_started&skip=0&limit=10
GET /api/tasks?assigned_to=1&sort_by=due_date
GET /api/tasks?overdue=true&sort_by=priority
```

### In Postman:
1. Open **Get All Tasks** request
2. Click **Params** tab
3. Add key-value pairs

| Key | Value | Purpose |
|-----|-------|---------|
| `status` | not_started, in_progress, completed | Filter by status |
| `assigned_to` | 1 | Filter by assignee |
| `created_by` | 1 | Filter by creator |
| `overdue` | true | Only overdue tasks |
| `sort_by` | created_at, due_date, priority | Sort option |
| `skip` | 0 | Pagination start |
| `limit` | 10 | Items per page |

---

## 📊 Dashboard Endpoints Explained

| Endpoint | Returns | Used For |
|----------|---------|----------|
| `GET /api/dashboard/stats` | Personal task stats | "How many tasks do I have?" |
| `GET /api/dashboard/team-stats` | All team statistics | "Team workload overview" |
| `GET /api/dashboard/summary` | Recent/upcoming/overdue | "What's important today?" |
| `GET /api/dashboard/user/{id}/workload` | Specific user's tasks | "How busy is John?" |

**Example Response**:
```json
{
  "total_tasks": 5,
  "completed_tasks": 2,
  "in_progress_tasks": 2,
  "not_started_tasks": 1,
  "overdue_tasks": 0,
  "completion_rate": 40.0
}
```

---

## 🧪 Testing Requests

### View Request Details
```
Headers → See auth headers
Body → See JSON being sent
Params → See query parameters
Pre-request Script → Code run before request
Tests → Code run after request
```

### Check Response
```
Status Code → 200 OK, 201 Created, 400 Bad Request, etc.
Response Body → JSON data returned
Response Headers → Server headers
Response Time → How long request took
```

---

## 🔗 URL Structure

Your collection uses variables:

```
{{base_url}} = http://localhost:8000
{{auth_token}} = Your JWT token
{{user_id}} = User ID (e.g., 1)
{{task_id}} = Task ID (e.g., 1)
```

### Example URLs:
```
GET {{base_url}}/api/tasks
POST {{base_url}}/api/tasks/{{task_id}}/move
GET {{base_url}}/api/dashboard/user/{{user_id}}/workload
```

---

## ✅ HTTP Status Codes Reference

| Code | Meaning | What Happened |
|------|---------|---------------|
| **200** | OK | Request succeeded ✅ |
| **201** | Created | Resource created ✅ |
| **204** | No Content | Deletion succeeded ✅ |
| **400** | Bad Request | Invalid data sent ❌ |
| **401** | Unauthorized | Missing/invalid token ❌ |
| **403** | Forbidden | Permission denied ❌ |
| **404** | Not Found | Resource doesn't exist ❌ |
| **500** | Server Error | Server problem ❌ |

---

## 🆘 Troubleshooting Checklist

| Problem | Check | Solution |
|---------|-------|----------|
| 401 Unauthorized | Token in headers | Re-login & update token |
| 404 Not Found | URL spelling | Verify endpoint path |
| Token expired | Token age | Re-login for new token |
| No response | API running? | Start: `uvicorn app.main:app --reload` |
| Invalid JSON | Request body | Check JSON syntax (use validator) |
| Database error | Database exists | Delete test.db, restart API |

---

## 📁 Folder Organization

```
Task Manager API
├── Authentication
│   ├── Register User
│   ├── Login User ← START HERE
│   └── Get Current User
├── User Management
│   ├── Get All Users
│   └── Get User by ID
├── Task Management
│   ├── Get All Tasks
│   ├── Create Task
│   ├── Get Task by ID
│   ├── Update Task
│   ├── Move Task ← JIRA FEATURE
│   └── Delete Task
├── Dashboard Analytics
│   ├── Get Personal Stats
│   ├── Get Team Stats
│   ├── Get Summary
│   └── Get User Workload
└── System
    ├── Health Check
    └── Root
```

---

## 🚀 One-Command Testing

```
1. Import collection
2. Set auth_token variable (from Login response)
3. Click Collection → Run
4. Select all folders
5. Click "Run" button
6. Watch all tests execute ✅
```

---

## 📝 Request Body Examples

### Create Task
```json
{
  "title": "New Task",
  "description": "Task description here",
  "priority": 3,
  "due_date": "2026-04-20T10:00:00",
  "assigned_to": 1
}
```

### Update Task
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "priority": 4,
  "assigned_to": 2
}
```

### Move Task (Jira-like)
```json
{
  "new_status": "in_progress",
  "new_position": 2
}
```

### Valid Statuses
- `not_started` - Initial state
- `in_progress` - Being worked on
- `completed` - Finished

---

## 💾 Working with Environments

### Create Environment
1. Environments (left sidebar) → **+**
2. Name: `Task Manager Dev`
3. Add variables:

```
base_url: http://localhost:8000
auth_token: (gets set after login)
user_id: 1
task_id: 1
```

### Switch Environment
- Top-right corner → Select environment
- All `{{variable}}` references update automatically

---

## 🔄 Updating Collection

### After API Changes
```bash
1. Update request in Postman
2. Right-click collection → Export
3. Save JSON file to project
4. git add Task_Manager_API.postman_collection.json
5. git commit -m "Update collection"
6. git push
```

### Team Gets Updates
```bash
git pull origin master
# Collection updated locally
# Re-import if needed
```

---

## 📞 Quick Support

| Issue | Solution |
|-------|----------|
| "How do I authenticate?" | See: **Authentication Setup** above |
| "This endpoint returns 401" | Token expired - re-login |
| "I want to test everything" | Click: Collection → Run |
| "How do I organize requests?" | Create Postman Environments |
| "Can I automate tests?" | Yes - add Tests tab code |
| "How do teammates use this?" | Share collection file via git |

---

## 🎓 Learning Resources

- **Postman Docs**: https://learning.postman.com/
- **API Docs**: http://localhost:8000/docs (Swagger)
- **This Project**: See README.md for full documentation
- **Postman Collection**: `Task_Manager_API.postman_collection.json`

---

**You're all set! Import the collection and start testing your APIs!** 🚀

---

## 🚀 One-Command Testing

```
1. Import collection
2. Set auth_token variable (from Login response)
3. Click Collection → Run
4. Select all folders
5. Click "Run" button
6. Watch all tests execute ✅
```

---

## 📝 Request Body Examples

### Create Task
```json
{
  "title": "New Task",
  "description": "Task description here",
  "priority": 3,
  "due_date": "2026-04-20T10:00:00",
  "assigned_to": 1
}
```

### Update Task
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "priority": 4,
  "assigned_to": 2
}
```

### Move Task (Jira-like)
```json
{
  "new_status": "in_progress",
  "new_position": 2
}
```

### Valid Statuses
- `not_started` - Initial state
- `in_progress` - Being worked on
- `completed` - Finished

---

## 💾 Working with Environments

### Create Environment
1. Environments (left sidebar) → **+**
2. Name: `Task Manager Dev`
3. Add variables:

```
base_url: http://localhost:8000
auth_token: (gets set after login)
user_id: 1
task_id: 1
```

### Switch Environment
- Top-right corner → Select environment
- All `{{variable}}` references update automatically

---

## 🔄 Updating Collection

### After API Changes
```bash
1. Update request in Postman
2. Right-click collection → Export
3. Save JSON file to project
4. git add Task_Manager_API.postman_collection.json
5. git commit -m "Update collection"
6. git push
```

### Team Gets Updates
```bash
git pull origin master
# Collection updated locally
# Re-import if needed
```

---

## 📞 Quick Support

| Issue | Solution |
|-------|----------|
| "How do I authenticate?" | See: **Authentication Setup** above |
| "This endpoint returns 401" | Token expired - re-login |
| "I want to test everything" | Click: Collection → Run |
| "How do I organize requests?" | Create Postman Environments |
| "Can I automate tests?" | Yes - add Tests tab code |
| "How do teammates use this?" | Share collection file via git |

---

## 🎓 Learning Resources

- **Postman Docs**: https://learning.postman.com/
- **API Docs**: http://localhost:8000/docs (Swagger)
- **This Project**: See README.md for full documentation
- **Postman Collection**: `Task_Manager_API.postman_collection.json`

---

**You're all set! Import the collection and start testing your APIs!** 🚀
