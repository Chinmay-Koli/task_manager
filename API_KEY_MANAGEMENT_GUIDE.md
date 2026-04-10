# 🔑 API KEY MANAGEMENT GUIDE

## Overview

Your Task Manager API now includes a complete **API Key Management System** for:
- ✅ Third-party integrations
- ✅ Service-to-service authentication
- ✅ Long-lived access without password sharing
- ✅ Granular permission control
- ✅ Key rotation and expiration
- ✅ Usage tracking

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Creating API Keys](#creating-api-keys)
3. [Using API Keys](#using-api-keys)
4. [Managing API Keys](#managing-api-keys)
5. [Permissions](#permissions)
6. [Security Best Practices](#security-best-practices)
7. [API Endpoints](#api-endpoints)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Step 1: Create an API Key

```bash
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Integration",
    "expires_in_days": 90,
    "can_read_tasks": true,
    "can_create_tasks": true,
    "can_update_tasks": true,
    "can_delete_tasks": false,
    "can_read_dashboard": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Mobile App Integration",
  "api_key": "tm_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "prefix": "tm_a1b2c3",
  "expires_at": "2026-07-09T12:34:56.789000",
  "created_at": "2026-04-10T12:34:56.789000"
}
```

**⚠️ IMPORTANT**: The full API key is shown **only once**! Save it securely. You won't be able to see it again.

### Step 2: Use the API Key

Use the API key in the `X-API-Key` header:

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

### Step 3: List Your API Keys

```bash
curl -X GET http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Creating API Keys

### What is an API Key?

An API Key is a long, random string that works like a password for automated systems:
- Doesn't expire by default (but can be set to expire)
- Can be restricted to specific permissions
- Can be revoked instantly
- Tracked for security audits

### Format

API keys use this format:
```
tm_[64-character-hex-string]
```

Example:
```
tm_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

The `tm_` prefix identifies it as a Task Manager API key.

### Creating an API Key

**Endpoint**: `POST /api/api-keys`

**Required Fields**:
- `name` - Friendly name for the key (e.g., "Mobile App", "CI/CD", "Bot")

**Optional Fields**:
- `expires_in_days` - Auto-expire after N days (1-365, default: never expires)
- `can_read_tasks` - Read task data (default: true)
- `can_create_tasks` - Create new tasks (default: true)
- `can_update_tasks` - Update task data (default: true)
- `can_delete_tasks` - Delete tasks (default: false)
- `can_read_dashboard` - Access dashboard/analytics (default: true)

**Example:**

```json
POST /api/api-keys
{
  "name": "Third-party Integration",
  "expires_in_days": 30,
  "can_read_tasks": true,
  "can_create_tasks": true,
  "can_update_tasks": false,
  "can_delete_tasks": false,
  "can_read_dashboard": false
}
```

---

## Using API Keys

### Authentication Methods

Your API supports **2 authentication methods**:

#### 1. JWT Token (for users)
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

#### 2. API Key (for services)
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_a1b2c3d4e5f6..."
```

### Priority

If both JWT token and API key are provided, **JWT token takes priority**.

### Making Requests with API Keys

#### Example 1: Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Automated Task",
    "description": "Created by automated system",
    "priority": 3
  }'
```

#### Example 2: Get All Tasks

```bash
curl -X GET "http://localhost:8000/api/tasks?status=in_progress" \
  -H "X-API-Key: tm_your_api_key"
```

#### Example 3: Update a Task

```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "X-API-Key: tm_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task",
    "priority": 4
  }'
```

#### Example 4: Move Task (Jira-like)

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/move \
  -H "X-API-Key: tm_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "in_progress",
    "new_position": 0
  }'
```

---

## Managing API Keys

### List All API Keys

View all your API keys (without exposing full key):

```bash
curl -X GET http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Mobile App",
    "prefix": "tm_a1b2c3",
    "is_active": true,
    "created_at": "2026-04-10T12:34:56.789000",
    "last_used_at": "2026-04-10T15:45:30.123000",
    "expires_at": "2026-07-09T12:34:56.789000",
    "can_read_tasks": true,
    "can_create_tasks": true,
    "can_update_tasks": true,
    "can_delete_tasks": false,
    "can_read_dashboard": true
  }
]
```

### Get API Key Details

```bash
curl -X GET http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Disable/Enable API Key

**Disable** (key stops working):
```bash
curl -X POST http://localhost:8000/api/api-keys/1/disable \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Enable** (key works again):
```bash
curl -X POST http://localhost:8000/api/api-keys/1/enable \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update API Key

Change name, permissions, or settings:

```bash
curl -X PATCH http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App v2",
    "can_delete_tasks": true
  }'
```

### Check API Key Usage

See when the key was last used and expiration status:

```bash
curl -X GET http://localhost:8000/api/api-keys/1/usage \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "name": "Mobile App",
  "prefix": "tm_a1b2c3",
  "created_at": "2026-04-10T12:34:56.789000",
  "last_used_at": "2026-04-10T15:45:30.123000",
  "expires_at": "2026-07-09T12:34:56.789000",
  "is_active": true,
  "days_since_creation": 5,
  "days_until_expiration": 90,
  "is_expired": false
}
```

### Revoke/Delete API Key

Permanently delete an API key (cannot be undone):

```bash
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

⚠️ **IMPORTANT**: Set `"confirm": true` to prevent accidental deletion.

---

## Permissions

### Permission Types

Each API key can have granular permissions:

| Permission | Description | Use Case |
|-----------|-------------|----------|
| `can_read_tasks` | Read all tasks, filtering | Dashboards, reporting tools |
| `can_create_tasks` | Create new tasks | Automation, integrations |
| `can_update_tasks` | Update task details | Task management bots |
| `can_delete_tasks` | Delete tasks | Admin operations only |
| `can_read_dashboard` | Access analytics/dashboard | Analytics integrations |

### Restriction Examples

#### API Key for Read-Only Dashboard Access
```json
{
  "name": "Dashboard Monitor",
  "can_read_tasks": true,
  "can_create_tasks": false,
  "can_update_tasks": false,
  "can_delete_tasks": false,
  "can_read_dashboard": true
}
```

#### API Key for Automated Task Creation
```json
{
  "name": "Automation Bot",
  "can_read_tasks": true,
  "can_create_tasks": true,
  "can_update_tasks": true,
  "can_delete_tasks": false,
  "can_read_dashboard": false
}
```

#### API Key for CI/CD Integration
```json
{
  "name": "CI/CD Pipeline",
  "can_read_tasks": true,
  "can_create_tasks": false,
  "can_update_tasks": true,
  "can_delete_tasks": false,
  "can_read_dashboard": false
}
```

---

## Security Best Practices

### ✅ DO

1. **Store keys securely**
   - Use environment variables
   - Never commit to version control
   - Use secrets management systems (AWS Secrets Manager, GitHub Secrets, etc.)

2. **Use environment variables** in your code:
   ```bash
   export TASK_MANAGER_API_KEY="tm_your_key"
   ```
   
   Then in your code:
   ```python
   import os
   api_key = os.getenv("TASK_MANAGER_API_KEY")
   ```

3. **Restrict permissions** - Only grant permissions needed
   - Create separate keys for different purposes
   - Don't enable `can_delete_tasks` unless necessary

4. **Set expiration dates**
   - Use `expires_in_days` to auto-revoke keys after period
   - Rotate keys (create new ones, delete old ones)
   - Example: 30-90 days is typical

5. **Monitor key usage**
   - Check `last_used_at` regularly
   - Investigate unexpected usage patterns
   - Use API key usage endpoints for audits

6. **Rotate keys periodically**
   - Create new key
   - Update applications to use new key
   - Delete old key
   - Repeat every 3-6 months

7. **Use version control for `.gitignore`**
   ```
   # .gitignore
   .env
   .env.local
   secrets.json
   *.key
   ```

### ❌ DON'T

1. **Never hardcode API keys** in source code
2. **Never share API keys** via email, chat, or public URLs
3. **Don't commit keys** to Git (even if deleted later)
4. **Don't use same key** for multiple applications
5. **Don't expose keys** in error messages or logs
6. **Don't grant unnecessary permissions**
7. **Don't forget to revoke** old/unused keys

### Security Headers

Always use HTTPS in production:
```
✅ https://api.example.com/api/tasks
❌ http://api.example.com/api/tasks
```

---

## API Endpoints

### Complete API Key Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/api/api-keys` | Create new API key |
| **GET** | `/api/api-keys` | List all your API keys |
| **GET** | `/api/api-keys/{id}` | Get specific key details |
| **PATCH** | `/api/api-keys/{id}` | Update key settings |
| **DELETE** | `/api/api-keys/{id}` | Revoke/delete key |
| **POST** | `/api/api-keys/{id}/disable` | Temporarily disable key |
| **POST** | `/api/api-keys/{id}/enable` | Re-enable disabled key |
| **GET** | `/api/api-keys/{id}/usage` | View key usage stats |

---

## Examples

### Example 1: Node.js / JavaScript

```javascript
// Store key in environment variable
const API_KEY = process.env.TASK_MANAGER_API_KEY;

// Create a task
async function createTask() {
  const response = await fetch('http://localhost:8000/api/tasks', {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: 'My Task',
      description: 'Task from Node.js',
      priority: 3
    })
  });
  
  const task = await response.json();
  console.log('Task created:', task);
}

createTask();
```

### Example 2: Python

```python
import os
import requests

API_KEY = os.getenv('TASK_MANAGER_API_KEY')
BASE_URL = 'http://localhost:8000'

# Create a task
def create_task():
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'title': 'My Python Task',
        'description': 'Task from Python',
        'priority': 3
    }
    
    response = requests.post(
        f'{BASE_URL}/api/tasks',
        headers=headers,
        json=data
    )
    
    print('Task created:', response.json())

create_task()
```

### Example 3: cURL (Bash)

```bash
# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "X-API-Key: $TASK_MANAGER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bash Task",
    "description": "Task from bash script",
    "priority": 3
  }'

# List all tasks
curl -X GET http://localhost:8000/api/tasks \
  -H "X-API-Key: $TASK_MANAGER_API_KEY"
```

### Example 4: API Key Rotation Script

```bash
#!/bin/bash

# 1. Create new API key
echo "Creating new API key..."
NEW_KEY=$(curl -s -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rotated Key - 2026-04",
    "expires_in_days": 90
  }' | jq -r '.api_key')

echo "New key created: ${NEW_KEY:0:10}..."

# 2. Update your application with new key
echo "Updating application..."
export TASK_MANAGER_API_KEY="$NEW_KEY"

# 3. Delete old key
echo "Removing old key..."
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

echo "Key rotation complete!"
```

---

## Troubleshooting

### Issue: "Invalid API key"

**Cause**: API key is incorrect or doesn't exist

**Solution**:
1. Verify API key is correct (copy-paste carefully)
2. Check key hasn't been revoked
3. Check key hasn't expired
4. Create a new key if necessary

### Issue: "API key is inactive"

**Cause**: Key was disabled

**Solution**:
1. Check if key is disabled: `GET /api/api-keys/{id}`
2. Re-enable: `POST /api/api-keys/{id}/enable`
3. Or create new key

### Issue: "API key has expired"

**Cause**: Key's expiration date passed

**Solution**:
1. Check expiration: `GET /api/api-keys/{id}/usage`
2. Create new key with longer expiration
3. Update applications to use new key

### Issue: "Permission denied" even with valid key

**Cause**: API key lacks required permission

**Solution**:
1. Check key permissions: `GET /api/api-keys/{id}`
2. Update permissions: `PATCH /api/api-keys/{id}`
3. Or create new key with required permissions

### Issue: Lost the API key (showed it only once!)

**Cause**: Didn't save the key when it was created

**Solution**:
1. Delete the old key: `DELETE /api/api-keys/{id}`
2. Create a new key
3. Save it securely this time!

---

## FAQs

**Q: How many API keys can I create?**
A: Unlimited! Create as many as you need for different integrations.

**Q: Can I change an API key after creation?**
A: No, but you can create a new key and delete the old one.

**Q: How do I reset an API key?**
A: Delete it and create a new one with the same name.

**Q: What happens if my API key is leaked?**
A: Immediately revoke it (DELETE endpoint) and create a new one.

**Q: Can API keys be used for user login?**
A: No, only for API access. Users must login with password to get JWT token.

**Q: Do API keys work with Postman?**
A: Yes! Set `X-API-Key` header in Postman or use environment variables.

**Q: How do I know if my key is being used?**
A: Check `last_used_at` with the usage endpoint.

---

## Summary

✅ **What You Have**:
- Secure API key generation
- Granular permission control
- Key expiration & rotation
- Usage tracking
- Easy key management

✅ **Best Practices**:
- Store keys in environment variables
- Set expiration dates
- Restrict permissions
- Rotate keys periodically
- Monitor usage

✅ **Integration Ready**:
- Third-party apps
- Automation workflows
- CI/CD pipelines
- Mobile apps
- IoT devices

Start creating and managing API keys today! 🔐
