# 🚀 API KEY INTEGRATION CHECKLIST

Use this checklist to implement API key management in your projects.

---

## ✅ Pre-Deployment

- [ ] API running successfully: `python -m uvicorn app.main:app --reload`
- [ ] Test script passes: `python setup_api_keys.py`
- [ ] Database table created: `api_keys` table exists
- [ ] All imports working without errors
- [ ] No migration needed (automatic via SQLAlchemy)

---

## ✅ For Developers

### Setup

- [ ] API key management system implemented
- [ ] Read `API_KEY_MANAGEMENT_GUIDE.md`
- [ ] Read `API_KEY_QUICK_START.md`
- [ ] Review `app/routes/api_keys.py` source
- [ ] Run `setup_api_keys.py` to test

### Database

- [ ] `api_keys` table exists in database
- [ ] All 11 fields properly created
- [ ] Indexes created for performance
- [ ] Foreign key to users table

### Code

- [ ] `app/models.py` has APIKey model
- [ ] `app/auth.py` has API key functions
- [ ] `app/schemas.py` has API key schemas
- [ ] `app/routes/api_keys.py` has 8 endpoints
- [ ] `app/main.py` includes api_keys router

---

## ✅ For Your Applications

### Using API Keys in Python

```python
# 1. Install requests if needed
# pip install requests

# 2. Create app with API key
import requests
import os

api_key = os.getenv('TASK_MANAGER_API_KEY')

headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}

# 3. Make requests
response = requests.get(
    'http://localhost:8000/api/tasks',
    headers=headers
)

tasks = response.json()
print(f"Total tasks: {len(tasks)}")
```

- [ ] Store API key in .env file
- [ ] Load from environment variable
- [ ] Add X-API-Key header to requests
- [ ] Test with sample endpoint

### Using API Keys in Node.js

```javascript
// 1. Install axios if needed
// npm install axios

// 2. Create app with API key
const axios = require('axios');

const api_key = process.env.TASK_MANAGER_API_KEY;

const headers = {
  'X-API-Key': api_key,
  'Content-Type': 'application/json'
};

// 3. Make requests
axios.get('http://localhost:8000/api/tasks', { headers })
  .then(res => console.log(`Total tasks: ${res.data.length}`))
  .catch(err => console.error(err));
```

- [ ] Store API key in .env file
- [ ] Load from environment variable
- [ ] Add X-API-Key header to requests
- [ ] Test with sample endpoint

### Using API Keys in Bash/cURL

```bash
# 1. Create .env file
echo "TASK_MANAGER_API_KEY=tm_your_key" > .env

# 2. Source it
source .env

# 3. Make requests
curl -H "X-API-Key: $TASK_MANAGER_API_KEY" \
  http://localhost:8000/api/tasks
```

- [ ] Create .env file with API_KEY
- [ ] Source the file in scripts
- [ ] Use in curl requests
- [ ] Test with sample endpoint

---

## ✅ For Your First API Key

### Step 1: Create via Postman

- [ ] Login to get JWT token
- [ ] Go to API Keys folder
- [ ] Send Create API Key request
- [ ] Copy the full `api_key` value
- [ ] Store it securely

### Step 2: Create via cURL

```bash
# Get JWT token first
JWT_TOKEN=$(curl -s -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_pass"}' \
  | jq -r '.access_token')

# Create API key
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First API Key",
    "expires_in_days": 90,
    "can_read_tasks": true,
    "can_create_tasks": true,
    "can_update_tasks": true,
    "can_delete_tasks": false,
    "can_read_dashboard": true
  }' | jq -r '.api_key'
```

- [ ] Execute commands
- [ ] Copy the returned API key
- [ ] Save to secure location

### Step 3: Test It

```bash
# Set key to environment variable
export TASK_MANAGER_API_KEY="tm_..."

# Test with endpoint
curl -H "X-API-Key: $TASK_MANAGER_API_KEY" \
  http://localhost:8000/api/tasks
```

- [ ] API key works with GET requests
- [ ] API key works with POST requests
- [ ] API key works with PUT requests
- [ ] API key properly rejected if invalid

---

## ✅ For Security

### Key Management

- [ ] Generated unique API key
- [ ] Key stored OUTSIDE version control
- [ ] Added to .gitignore
- [ ] Key not in environment variables shown in docs
- [ ] Key not in commit history
- [ ] Key not in error logs

### Key Rotation

- [ ] Plan rotation schedule (every 90 days recommended)
- [ ] Create new key: `POST /api/api-keys`
- [ ] Update applications to use new key
- [ ] Delete old key: `DELETE /api/api-keys/{id}`
- [ ] Verify old key no longer works

### Key Monitoring

- [ ] Monitor `last_used_at` timestamp
- [ ] Alert on unused keys (stale keys)
- [ ] Alert on suspicious usage patterns
- [ ] Track permissions needed vs granted
- [ ] Disable rather than delete when testing

### .env File Security

```bash
# .env file content
TASK_MANAGER_API_KEY=tm_abc123...
TASK_MANAGER_URL=http://localhost:8000

# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets.json" >> .gitignore
```

- [ ] .env file is in .gitignore
- [ ] .env file not committed to git
- [ ] .env file never shared
- [ ] .env variables documented in .env.example

---

## ✅ For Different Use Cases

### Use Case 1: Third-party Integration

```python
# E.g., Zapier, IFTTT, or custom integration

api_key = os.getenv('TASK_MANAGER_API_KEY')

# Create task from external service
requests.post(
  'http://localhost:8000/api/tasks',
  headers={'X-API-Key': api_key},
  json={
    'title': 'Task from third party',
    'description': 'Automatically created',
    'priority': 3
  }
)
```

- [ ] API key created with limited permissions
- [ ] Only `can_read_tasks` and `can_create_tasks` enabled
- [ ] `can_delete_tasks` is FALSE
- [ ] Set expiration date (30-60 days)
- [ ] Integration tested and working

### Use Case 2: CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Update task status
        run: |
          curl -H "X-API-Key: ${{ secrets.TASK_API_KEY }}" \
            -X PATCH http://api.example.com/api/tasks/1/move \
            -H "Content-Type: application/json" \
            -d '{
              "new_status": "completed",
              "new_position": 0
            }'
```

- [ ] API key stored in GitHub Secrets
- [ ] Key not printed in logs
- [ ] Only `can_read_tasks` and `can_update_tasks` enabled
- [ ] `can_delete_tasks` FALSE, `can_create_tasks` FALSE
- [ ] Test pipeline runs successfully

### Use Case 3: Mobile App

```javascript
// React Native / Flutter app

const api_key = await AsyncStorage.getItem('api_key');

// Create headers for all requests
const headers = {
  'X-API-Key': api_key,
  'Content-Type': 'application/json'
};

// Use in all API calls
fetch('http://api.example.com/api/tasks', { headers })
  .then(res => res.json())
  .then(data => setTasks(data));
```

- [ ] API key created specifically for mobile
- [ ] Key stored securely in app storage
- [ ] Permissions: read, create, update (no delete)
- [ ] Expiration set to 180 days or never
- [ ] User can view/revoke from settings

### Use Case 4: Bot/Automation

```python
# Scheduled task runner

import schedule
import time

def scheduled_task():
    api_key = os.getenv('TASK_MANAGER_API_KEY')
    
    # Get tasks due today
    response = requests.get(
        'http://localhost:8000/api/tasks?overdue=true',
        headers={'X-API-Key': api_key}
    )
    
    for task in response.json():
        # Send notification
        notify_user(task)
        
        # Update status
        requests.patch(
            f'http://localhost:8000/api/tasks/{task["id"]}/move',
            headers={'X-API-Key': api_key},
            json={
                'new_status': 'in_progress',
                'new_position': 0
            }
        )

# Run every hour
schedule.every().hour.do(scheduled_task)
while True:
    schedule.run_pending()
    time.sleep(1)
```

- [ ] API key created for bot
- [ ] Permissions: read, create, update
- [ ] `can_delete_tasks` FALSE
- [ ] Expiration set reasonably (30-90 days)
- [ ] Bot runs successfully without errors

---

## ✅ For Troubleshooting

If API key doesn't work:

- [ ] Verify API is running: `GET /health` returns 200
- [ ] Check API key format starts with `tm_`
- [ ] Verify header name is exactly `X-API-Key`
- [ ] Confirm key hasn't been deleted/revoked
- [ ] Confirm key isn't expired: `GET /api/api-keys/{id}/usage`
- [ ] Verify key is active: `GET /api/api-keys/{id}`
- [ ] Check permissions allow the requested operation
- [ ] Re-create key if unsure (old key lost?)

If authentication fails:

- [ ] Try with JWT token instead: `Authorization: Bearer {token}`
- [ ] Ensure both aren't malformed
- [ ] Check Application accepts the authentication method
- [ ] Verify header is sent with every request

---

## ✅ For Postman Users

### Setup API Key in Postman

1. Go to API Keys folder
2. Click "Create API Key" request
3. Make sure authenticated with JWT token
4. Click **Send**
5. Copy the `api_key` value
6. Go to **Collections** → (collection name) → **Variables**
7. Find `api_key_value` or create it
8. Paste the value in **Current Value**
9. Click **Save**
10. All requests with `X-API-Key` header now auto-populate

### Or Set in Pre-request Script

```javascript
// In "Create API Key" request → Tests tab:

if(pm.response.code === 201) {
    let response = pm.response.json();
    pm.environment.set("api_key_value", response.api_key);
}
```

- [ ] Pre-request script auto-saves key
- [ ] Key available in all subsequent requests
- [ ] X-API-Key header uses {{api_key_value}}
- [ ] All tests pass

---

## ✅ For Production Deployment

Before going live:

- [ ] API running on production server
- [ ] Database securely configured
- [ ] HTTPS enabled (not HTTP)
- [ ] API keys not logged in output
- [ ] Rate limiting implemented
- [ ] Key rotation policy in place
- [ ] Monitoring/alerts configured
- [ ] Backup strategy documented
- [ ] API documentation updated
- [ ] Team trained on API key usage

---

## ✅ Documentation

- [ ] Read `API_KEY_MANAGEMENT_GUIDE.md` (comprehensive)
- [ ] Read `API_KEY_QUICK_START.md` (quick reference)
- [ ] Saved `API_KEY_IMPLEMENTATION_SUMMARY.md` for reference
- [ ] Bookmarked `/docs` endpoint for API reference
- [ ] Reviewed examples for your programming language
- [ ] Understood security best practices
- [ ] Know how to rotate keys
- [ ] Know how to revoke keys

---

## ✅ Team Communication

If sharing with team:

- [ ] Shared API base URL
- [ ] Shared how to create API key
- [ ] Sent link to `API_KEY_QUICK_START.md`
- [ ] **DID NOT share any actual API keys**
- [ ] Each team member created their own key
- [ ] Documented usage policies
- [ ] Set up key rotation schedule
- [ ] Established monitoring/alerting

---

## ✅ Final Verification

```bash
# 1. API running
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# 2. Can create API key (with JWT)
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $JWT"
# Expected: 201 Created with full key shown

# 3. Can use API key
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/tasks
# Expected: 200 OK with tasks

# 4. Invalid key rejected
curl -H "X-API-Key: invalid" \
  http://localhost:8000/api/tasks
# Expected: 401 Unauthorized
```

- [ ] API health check passes
- [ ] Can create API key
- [ ] Can use API key
- [ ] Invalid key is rejected

---

## 🎉 Success!

You now have a complete, secure API key management system!

### Summary of What You Have

✅ 8 endpoints for API key management  
✅ Dual authentication (JWT + API key)  
✅ Granular permission control  
✅ Secure key hashing (SHA-256)  
✅ Usage tracking  
✅ Expiration support  
✅ Complete documentation  
✅ Test script included  

### Next Steps

1. Run `python setup_api_keys.py` to verify everything works
2. Create your first API key
3. Test with at least one application
4. Store key securely
5. Start using for integrations!

---

**Questions?** See the comprehensive guide: `API_KEY_MANAGEMENT_GUIDE.md`
