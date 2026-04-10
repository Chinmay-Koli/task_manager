# Postman Collection Management Guide

## 📋 Overview

Your project includes a complete Postman collection: **`Task_Manager_API.postman_collection.json`**

This guide covers:
- ✅ How to import the collection
- ✅ How to organize and use it
- ✅ How to maintain authentication
- ✅ How to update endpoints
- ✅ Best practices for team collaboration

---

## 1️⃣ Importing the Collection

### Method 1: Using Import Button (Easiest)

1. **Open Postman** (download from https://www.postman.com/downloads/ if needed)
2. Click **Import** (top-left corner)
3. Choose **Upload Files** tab
4. Select: `Task_Manager_API.postman_collection.json`
5. Click **Import**

**Result**: All 26 endpoints organized into folders appear in your workspace

### Method 2: Using File Drop

1. Open Postman
2. Drag & drop `Task_Manager_API.postman_collection.json` into the Postman window
3. Click **Import** in the dialog

### Method 3: From Workspace

1. Postman → Collections (left sidebar)
2. Click **+** button
3. Select **Import** 
4. Choose the collection file

---

## 2️⃣ Collection Structure

Your collection is organized into folders:

```
Task Manager API - Jira-like
├── 📂 Authentication (3 endpoints)
│   ├── Register User
│   ├── Login User
│   └── Get Current User
├── 📂 User Management (2 endpoints)
│   ├── Get All Users
│   └── Get User by ID
├── 📂 Task Management (6 endpoints)
│   ├── Get All Tasks
│   ├── Create Task
│   ├── Get Task by ID
│   ├── Update Task
│   ├── Move Task (Jira-like)
│   └── Delete Task
├── 📂 Dashboard Analytics (4 endpoints)
│   ├── Get Personal Dashboard Stats
│   ├── Get Team Dashboard Stats
│   ├── Get Personal Dashboard Summary
│   └── Get User Workload
└── 📂 System (2 endpoints)
    ├── Health Check
    └── Root
```

---

## 3️⃣ Setting Up Authentication (CRITICAL)

The collection uses Postman **Variables** for authentication. Follow these steps:

### Step 1: Login First

1. Go to **Authentication** folder → **Login User**
2. Click **Send**
3. Response shows: `"access_token": "eyJhbGc..."`
4. Copy the entire token value (without quotes)

### Step 2: Set Collection Variable

1. Go to collection name → **Variables** tab
2. Find or create `auth_token` variable
3. Paste token in **Current Value** column
4. Click **Save**

**OR** (Better way - Automatic):

### Automated Token Setup (Recommended)

1. Select **Login User** request
2. Go to **Tests** tab
3. Add this code:
```javascript
if (pm.response.code === 200) {
    let response = pm.response.json();
    pm.collectionVariables.set("auth_token", response.access_token);
}
```
4. Send request
5. Token automatically saves to `{{auth_token}}`

Now all protected endpoints automatically use this token!

---

## 4️⃣ Running a Complete Workflow

### Scenario: Create User → Login → Create Task → Move Task

#### Step 1: Register User
1. Go to **Authentication** → **Register User**
2. Edit body with your credentials:
```json
{
  "username": "your_username",
  "email": "you@example.com",
  "full_name": "Your Name",
  "password": "SecurePass123"
}
```
3. Click **Send** ✅

#### Step 2: Login
1. Go to **Authentication** → **Login User**
2. Edit body with the username/password you just created
3. Click **Send**
4. Copy the `access_token` from response
5. Set it in Variables (see Step 3)

#### Step 3: Create Task
1. Go to **Task Management** → **Create Task**
2. Edit body:
```json
{
  "title": "My First Task",
  "description": "Task description",
  "priority": 3,
  "due_date": "2026-04-20T10:00:00",
  "assigned_to": 1
}
```
3. Click **Send** ✅
4. Copy the `id` from response

#### Step 4: Move Task
1. Go to **Task Management** → **Move Task**
2. Replace `{task_id}` URL with the ID you got
3. Edit body:
```json
{
  "new_status": "in_progress",
  "new_position": 0
}
```
4. Click **Send** ✅

---

## 5️⃣ Using Query Parameters

Many endpoints support filtering. Examples:

### Filter Tasks by Status
```
GET /api/tasks?status=not_started
GET /api/tasks?status=in_progress
GET /api/tasks?status=completed
```

In Postman:
1. Open **Get All Tasks** request
2. Go to **Params** tab
3. Add key-value pairs:
   - `status` = `not_started`
   - `skip` = `0`
   - `limit` = `10`

### Filter by Assignee
```
GET /api/tasks?assigned_to=1&status=in_progress
```

### Filter Overdue Tasks
```
GET /api/tasks?overdue=true
```

### Sort Options
```
GET /api/tasks?sort_by=due_date
GET /api/tasks?sort_by=priority
GET /api/tasks?sort_by=position
```

---

## 6️⃣ Environment Management

### Create a Postman Environment

1. Go to **Environments** (left sidebar)
2. Click **+** (Create new)
3. Name it: `Task Manager Dev`
4. Add variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | http://localhost:8000 | http://localhost:8000 |
| `auth_token` | "" | (gets set after login) |
| `user_id` | 1 | 1 |
| `task_id` | 1 | (gets set after task creation) |

### Using Environment Variables

Replace hardcoded URLs with `{{base_url}}`:
- Instead of: `http://localhost:8000/api/tasks`
- Use: `{{base_url}}/api/tasks`

**Benefits**:
- ✅ Easy to switch between dev/staging/prod
- ✅ Store sensitive values
- ✅ Share with team securely

---

## 7️⃣ Pre-request Scripts (Automation)

Add these to automate common tasks:

### Auto-set Task ID from Response
1. Select **Create Task** request
2. Go to **Tests** tab
3. Add:
```javascript
if (pm.response.code === 201) {
    let response = pm.response.json();
    pm.collectionVariables.set("task_id", response.id);
}
```

### Auto-set User ID from Response
1. Select **Register User** request
2. Go to **Tests** tab
3. Add:
```javascript
if (pm.response.code === 200) {
    let response = pm.response.json();
    pm.collectionVariables.set("user_id", response.id);
}
```

---

## 8️⃣ Running Tests & Assertions

### Add Response Assertions

1. Select any request
2. Go to **Tests** tab
3. Add validation:

```javascript
// Check status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response has required field
pm.test("Response has access_token", function () {
    pm.response.to.have.jsonBody("access_token");
});

// Check response value
pm.test("User is active", function () {
    let response = pm.response.json();
    pm.expect(response.is_active).to.equal(true);
});
```

---

## 9️⃣ Collection Runner - Run All Tests

### Execute Entire Workflow

1. Click **Collection** → **Run** (play icon)
2. Select collection: `Task Manager API - Jira-like`
3. Choose folder (or run all)
4. Click **Run**

**Features**:
- ✅ Run endpoints in sequence
- ✅ View pass/fail for each request
- ✅ See response times
- ✅ Export test results

### Example: Run Only Task Management
1. **Collection Runner** → Select `Task Manager API`
2. Check only **Task Management** folder
3. Set iterations: 1
4. Click **Run**

---

## 🔟 Maintaining the Collection

### When to Update Collection

✅ **Add new endpoint**:
1. Open collection in editor
2. Right-click folder → **Add Request**
3. Name it, set method, URL, body
4. Save

✅ **Update existing endpoint**:
1. Click request
2. Modify URL, parameters, body
3. Save (Ctrl+S)

✅ **Export updated collection**:
1. Right-click collection
2. **Export**
3. Save updated JSON file to project

### Syncing with API Changes

When your API changes:
1. Update the Postman request
2. Test it
3. Export collection
4. Commit to git:
```bash
git add Task_Manager_API.postman_collection.json
git commit -m "Update Postman collection - add new endpoint"
git push
```

---

## 1️⃣1️⃣ Team Collaboration

### Share Collection with Team

#### Method 1: Via Git Repository
```bash
# Collection is already in git
git push origin master
# Team members can import from repo
```

#### Method 2: Postman Cloud Sync
1. Login to Postman account
2. Collections → **Sync to cloud**
3. Share link with team
4. Team imports collection

#### Method 3: Export & Email
1. Right-click collection → **Export**
2. Email JSON file to team
3. Team imports via **Import** button

### Version Control

Track collection changes:
```bash
# Before making changes
git pull origin master

# Make changes to collection

# Commit changes
git add Task_Manager_API.postman_collection.json
git commit -m "Add new dashboard endpoint to collection"
git push origin master
```

---

## 1️⃣2️⃣ Common Tasks

### Task: Test All Endpoints Quickly

1. **Import collection** into Postman
2. **Set environment** (auth token)
3. **Run Collection** → Select all folders
4. View results

### Task: Create New Test Scenario

1. **Duplicate request** (right-click)
2. **Modify** for new scenario
3. **Add to new folder** (Scenarios)
4. **Save** and run

### Task: Debug Failed Request

1. **Open request** that failed
2. Go to **Headers** tab → check `Authorization`
3. Go to **Params** tab → verify query parameters
4. Go to **Body** tab → check JSON format
5. Check **Console** (Ctrl+Alt+C) for errors
6. Click **Send** to retry

### Task: Export Collection Results

1. **Run Collection**
2. Click **Export Results** (bottom-right)
3. Save CSV file for reports/records

---

## 1️⃣3️⃣ Best Practices

✅ **DO**:
- Always use `{{variables}}` instead of hardcoding values
- Keep sensitive data in Environments, not the collection
- Add descriptions to each request
- Use meaningful folder names
- Test all endpoints before committing changes
- Export collection regularly and commit to git

❌ **DON'T**:
- Hardcode API tokens in collection (security risk)
- Leave test data with sensitive information
- Forget to update collection when API changes
- Share collections with credentials exposed
- Use different collection versions on different machines

---

## 1️⃣4️⃣ Troubleshooting

### Issue: "Could not validate credentials" (401)

**Solution**:
1. Go to **Login User** request
2. Send it (get new token)
3. Set `auth_token` variable
4. Try protected endpoint again

### Issue: "Cannot GET /api/tasks" (404)

**Solution**:
1. Check API is running: `uvicorn app.main:app --reload`
2. Verify URL is correct in request
3. Check `{{base_url}}` variable is set
4. Click **Send** again

### Issue: Requests Show "No response"

**Solution**:
1. Verify API server is running
2. Check network connection
3. Try different endpoint
4. Restart Postman

### Issue: Token Expired

**Solution**:
1. Go to **Login User** request
2. Send it to get fresh token
3. Variable auto-updates
4. Retry protected endpoint

---

## 1️⃣5️⃣ Quick Reference

### Most Used Endpoints

```bash
# Register & Login
POST {{base_url}}/api/users/register
POST {{base_url}}/api/users/login

# Create & Manage Tasks
POST {{base_url}}/api/tasks
GET {{base_url}}/api/tasks
PATCH {{base_url}}/api/tasks/{{task_id}}/move

# Dashboard
GET {{base_url}}/api/dashboard/stats
GET {{base_url}}/api/dashboard/team-stats
```

### Keyboard Shortcuts

- `Ctrl+S` - Save request
- `Ctrl+Alt+C` - Open Console (debugging)
- `Ctrl+Enter` - Send request
- `Ctrl+Shift+E` - Open Environment manager

---

## Summary

Your Postman collection is **ready to use**! 

**Quick Start**:
1. Import `Task_Manager_API.postman_collection.json`
2. Run **Login User** endpoint
3. Set token in variables
4. Use other endpoints

**Key Features**:
- ✅ 26 pre-configured endpoints
- ✅ Bearer token authentication
- ✅ Variable-based configuration
- ✅ Full environment support
- ✅ Test automation ready

For questions, check the API documentation at `/docs` (http://localhost:8000/docs)
