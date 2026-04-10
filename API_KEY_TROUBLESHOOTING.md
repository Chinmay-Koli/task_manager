# 🔧 API KEY TROUBLESHOOTING GUIDE

Quick fixes for common API key issues.

---

## ❌ Problem: "401 Unauthorized" Error

### Symptom
```
HTTP 401 Unauthorized
{"detail":"Not authenticated"}
```

### Root Causes & Solutions

**Cause 1: Missing X-API-Key Header**
```bash
# ❌ Wrong - No header
curl http://localhost:8000/api/tasks

# ✅ Correct - Has header
curl -H "X-API-Key: tm_abc123..." http://localhost:8000/api/tasks
```
- [ ] Add `-H "X-API-Key: YOUR_KEY"` to curl command
- [ ] Add header to your HTTP client library

**Cause 2: Wrong Header Name**
```bash
# ❌ Wrong - "API-Key" instead of "X-API-Key"
curl -H "API-Key: tm_abc123..." http://localhost:8000/api/tasks

# ✅ Correct - Exact name
curl -H "X-API-Key: tm_abc123..." http://localhost:8000/api/tasks
```
- [ ] Header name MUST be `X-API-Key` (case-sensitive)
- [ ] Case matters: `X-API-Key` not `x-api-key` or `API-Key`

**Cause 3: Invalid API Key Format**
```bash
# ❌ Wrong - Doesn't start with tm_
curl -H "X-API-Key: my_key" http://localhost:8000/api/tasks

# ✅ Correct - Starts with tm_
curl -H "X-API-Key: tm_abc123xyz..." http://localhost:8000/api/tasks
```
- [ ] API key MUST start with `tm_`
- [ ] Copy the ENTIRE key, not just part of it

**Cause 4: API Key Doesn't Exist**
```python
# Check if key exists
import requests

headers = {'X-API-Key': 'tm_abc123...'}
response = requests.get(
    'http://localhost:8000/api/api-keys/1',
    headers=headers
)

if response.status_code == 404:
    print("Key not found - may have been deleted")
```
- [ ] Verify API key hasn't been deleted
- [ ] Check if you're using the right key (multiple keys?)

**Cause 5: Using Revoked API Key**
```bash
# Check if key is active
curl -H "X-API-Key: FULL_KEY_HERE" \
  'http://localhost:8000/api/api-keys' | grep -A5 '"is_active": false'
```
- [ ] Look for `"is_active": false` in the response
- [ ] Create a new API key if current one is revoked
- [ ] Check email for revocation notice If shared key

---

## ❌ Problem: "403 Forbidden" Error

### Symptom
```
HTTP 403 Forbidden
{"detail":"Not enough permissions"}
```

### Root Causes & Solutions

**Cause 1: Missing Permission for Operation**

```python
# Example: Trying to DELETE without permission

# If key created with: can_delete_tasks = False
# This will fail:
requests.delete(
    'http://localhost:8000/api/tasks/1',
    headers={'X-API-Key': api_key}
)
# Response: 403 Forbidden

# Solution: Create key WITH delete permission
```

Permission Matrix:
| Operation | Permission Needed |
|-----------|-----------------|
| GET /api/tasks | `can_read_tasks` |
| POST /api/tasks | `can_create_tasks` |
| PUT/PATCH /api/tasks/{id} | `can_update_tasks` |
| DELETE /api/tasks/{id} | `can_delete_tasks` |
| GET /api/dashboard | `can_read_dashboard` |

- [ ] Check which permission the operation needs (see table)
- [ ] Verify key has that permission: `GET /api/api-keys/{id}`
- [ ] If not, create new key with needed permissions OR update existing key

**Fix: Update Permissions on Existing Key**

```bash
# PATCH the key to add permissions
curl -X PATCH http://localhost:8000/api/api-keys/1 \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "can_delete_tasks": true
  }' | jq '.'
```

- [ ] Use an admin API key to update
- [ ] Send only the permissions to change
- [ ] Test with updated key

---

## ❌ Problem: "API Key Expired" Error

### Symptom
```
HTTP 401 Unauthorized
{"detail":"API key has expired"}
```

### Root Causes & Solutions

**Check Expiration Date**
```bash
# Check when key expires
curl http://localhost:8000/api/api-keys/1 | jq '.expires_at'

# Response examples:
# null              → Never expires
# "2025-01-15..."   → Expires Jan 15, 2025
```

- [ ] Check `expires_at` field
- [ ] If date is in past, key is expired

**Fix 1: Create New Key**

```bash
# If old key expired, create new one
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Replacement Key",
    "expires_in_days": 90,
    "can_read_tasks": true,
    "can_create_tasks": true,
    "can_update_tasks": true,
    "can_delete_tasks": false,
    "can_read_dashboard": true
  }' | jq '.api_key'

# Copy new key and use in applications
```

- [ ] Create with appropriate `expires_in_days`
- [ ] Copy the new key
- [ ] Update all applications

**Fix 2: Extend Expiration (if possible)**

```bash
# Some systems allow extension without creating new key
# Currently not supported, so create new key instead
```

**Prevention: Key Rotation Policy**

```bash
# Set calendar reminders to rotate keys:
# 1. Create new key: 1 week before expiration
# 2. Update all applications to use new key
# 3. Delete old key after confirmation it's no longer used

# Example: 90-day keys
# Create new key on day 83
# Delete old key on day 91
```

- [ ] Set expiration to 30-90 days
- [ ] Calendar remind 1 week before expiration
- [ ] Create replacement key early
- [ ] Test new key before deleting old one

---

## ❌ Problem: "Key Not Found" Error When Listing

### Symptom
```
curl -H "X-API-Key: tm_abc123" http://localhost:8000/api/api-keys

# Returns empty list [] instead of showing your keys
```

### Root Causes & Solutions

**Cause 1: API Key Belongs to Different User**
```python
# If you created key with User A
# But logged in as User B
# You won't see User A's keys

# Fix: Make sure you're viewing keys for the right user
```

- [ ] Verify you created the key under your account
- [ ] Check if you're logged in as different user
- [ ] Create key under current user account

**Cause 2: Browser/Session Issue**
```bash
# Clear cookies and cookies in Postman

# In Postman:
# 1. Click "Cookies" at bottom
# 2. Delete all cookies for localhost:8000
# 3. Login again
# 4. Try listing keys
```

- [ ] Clear browser cookies
- [ ] Log out and log back in
- [ ] Try in different browser/incognito
- [ ] Try with curl to eliminate UI issues

**Cause 3: Key Deleted in Background**
```bash
# If another admin deleted it, it won't appear

# Check deletion in logs:
# Review my-app.log for deletion events
```

- [ ] Ask team if anyone deleted keys
- [ ] Check system logs for deletion events
- [ ] Create new key

---

## ❌ Problem: API Key Works in Postman, Not in Code

### Symptom
```
# Postman: Works fine ✅
# Python: "401 Unauthorized" ❌
# Node.js: "401 Unauthorized" ❌
```

### Root Causes & Solutions

**Cause 1: Header Name Wrong in Code**

```python
# ❌ Wrong
headers = {
    'api_key': api_key,  # ← Wrong header name
}

# ✅ Correct
headers = {
    'X-API-Key': api_key,  # ← Correct header name
}

response = requests.get(
    'http://localhost:8000/api/tasks',
    headers=headers
)
```

- [ ] Use `X-API-Key` (capital X, capital A, capital K)
- [ ] Not `api_key`, not `Api-Key`, not `API-Key`

**Cause 2: API Key Variable Wrong**

```python
# ❌ Wrong - using placeholder
api_key = 'YOUR_API_KEY'  # ← This is literal string!

# ✅ Correct - using environment variable
import os
api_key = os.getenv('TASK_MANAGER_API_KEY')

# ✅ Also correct - hardcoded (development only!)
api_key = 'tm_abc123xyz...'
```

- [ ] Don't use placeholder strings
- [ ] Load from environment variable or file
- [ ] Print `api_key` variable to debug: `print(f"Key: {api_key}")`

**Cause 3: Empty or None API Key**

```python
# Debug: Check if key is actually set

import os
api_key = os.getenv('TASK_MANAGER_API_KEY')

if not api_key:
    print("ERROR: API key not set!")
    print("Set it with: export TASK_MANAGER_API_KEY=tm_...")
else:
    print(f"✓ Key loaded: {api_key[:10]}...")  # Show first 10 chars
```

- [ ] Print key value to verify it's not None/empty
- [ ] Check if environment variable is actually set
- [ ] Verify .env file exists and is loaded

**Cause 4: String Has Extra Spaces**

```python
# ❌ Wrong - trailing space
api_key = 'tm_abc123 '  # ← Space at end!

# ✅ Correct - no spaces
api_key = 'tm_abc123'

# Debug: Check for spaces
print(f"Key length: {len(api_key)}")
print(f"Key repr: {repr(api_key)}")  # Shows hidden spaces
```

- [ ] Check for trailing/leading spaces
- [ ] Use `.strip()` when reading from file: `api_key = api_key.strip()`

**Cause 5: Connection Issue (localhost vs hostname)**

```python
# ❌ Wrong - can't reach server
requests.get(
    'http://192.168.1.100:8000/api/tasks',  # ← DNS resolution fails?
    headers={'X-API-Key': api_key}
)

# ✅ Correct - development
requests.get(
    'http://localhost:8000/api/tasks',
    headers={'X-API-Key': api_key}
)

# ✅ Correct - production
requests.get(
    'https://api.mycompany.com/api/tasks',
    headers={'X-API-Key': api_key}
)
```

- [ ] Verify API server is running
- [ ] Test connection: `curl http://localhost:8000/health`
- [ ] Check API URL is correct
- [ ] Use localhost for development, domain for production

---

## ❌ Problem: Key Works, But Returns Wrong User's Data

### Symptom
```
# User A creates key with User A data
# But can somehow see User B's tasks
# This is a SECURITY ISSUE!
```

### Root Causes & Solutions

**Note: This shouldn't happen with current implementation**

The API is designed to:
- Prevent cross-user access
- Each key is bound to specific user
- Each key can only access that user's data

**If this happens: It's a bug!**

```bash
# File issue with details:
# 1. User created
# 2. Key created
# 3. Unexpected data accessed
# 4. Steps to reproduce

# Do NOT use in production until fixed
```

---

## ❌ Problem: "Can't Delete Key - Confirmation Failed"

### Symptom
```
DELETE /api/api-keys/1

Response: 400 Bad Request
{"detail":"Confirmation required. Include `confirm: true`"}
```

### Root Causes & Solutions

**Cause: Missing Confirmation**

```bash
# ❌ Wrong - No confirmation
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "X-API-Key: $API_KEY"

# ✅ Correct - With confirmation
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

- [ ] Add confirmation flag: `{"confirm": true}`
- [ ] Include Content-Type header
- [ ] Verify key_id in URL is correct

---

## ❌ Problem: Performance Slow / Rate Limited

### Symptom
```
# Requests getting slow
# Or: 429 Too Many Requests (Rate Limited)
```

### Root Causes & Solutions

**Cause 1: Too Many Requests**

```bash
# If making 1000 requests/second, system will throttle

# Solution: Add delays between requests

# Python example:
import time
import requests

for task_id in range(1, 100):
    response = requests.get(
        f'http://localhost:8000/api/tasks/{task_id}',
        headers={'X-API-Key': api_key}
    )
    time.sleep(0.1)  # ← 100ms delay between requests
```

- [ ] Add delays between requests (10-100ms)
- [ ] Use batch operations if available
- [ ] Contact support if needing higher rate limits

**Cause 2: Database Under Load**

```bash
# Check database performance

# Monitor with:
# In terminal running API:
# Look for slow query warnings

# In database:
# SELECT count(*) FROM api_keys;  -- Check if too many keys
```

- [ ] Monitor database size
- [ ] Archive old keys if needed
- [ ] Contact DBA if performance issue

---

## ⚠️ Security Issues

### Issue 1: Key Leaked in Public Place

**If your API key is exposed:**

```bash
# 1. IMMEDIATELY disable the key
curl -X POST http://localhost:8000/api/api-keys/KEY_ID/disable \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json"

# 2. Check usage logs to see if compromised
curl http://localhost:8000/api/api-keys/KEY_ID/usage \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json" | jq '.'

# 3. Create new key
# 4. Update all applications
# 5. Delete old key

# 6. Audit what was accessed
# Check task/activity logs for suspicious access
```

- [ ] Disable key immediately
- [ ] Check usage logs
- [ ] Create new key
- [ ] Audit access logs
- [ ] Delete compromised key

### Issue 2: Key Hardcoded in Source Code

```bash
# ❌ NEVER DO THIS
# src/app.py contains:
API_KEY = 'tm_secret_key_here'  # ← EXPOSED TO EVERYONE!

# ✅ DO THIS INSTEAD
# 1. Remove from code
git remove --cached src/app.py  # Remove from history
git commit -m "Remove API key"

# 2. Rotate key (old one is compromised)
curl -X POST .../api-keys \
  -H "Authorization: Bearer $JWT" \
  -d {...}

# 3. Move to environment
# .env file (NOT committed):
TASK_MANAGER_API_KEY=tm_new_key...

# 4. Load in code
import os
api_key = os.getenv('TASK_MANAGER_API_KEY')
```

- [ ] Remove from source code immediately
- [ ] Rotate/create new key (old is compromised)
- [ ] Move to environment variable
- [ ] Add .env to .gitignore
- [ ] Review git history for exposed keys

---

## ✅ Debugging Tips

### Get Full Error Details

```bash
# Use -v flag for verbose output
curl -v -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/tasks 2>&1 | grep -A 20 "{}"
```

### Test Key Validity

```bash
# Create simple test script
python3 << 'EOF'
import requests
import os

api_key = os.getenv('TASK_MANAGER_API_KEY')

if not api_key:
    print("❌ API_KEY not set")
    exit(1)

headers = {'X-API-Key': api_key}

# Test 1: Health check
r1 = requests.get('http://localhost:8000/health')
print(f"1. Health: {r1.status_code}")

# Test 2: List tasks
r2 = requests.get('http://localhost:8000/api/tasks', headers=headers)
print(f"2. Tasks: {r2.status_code}")

# Test 3: Get key info
r3 = requests.get('http://localhost:8000/api/api-keys', headers=headers)
print(f"3. List keys: {r3.status_code}")

# Test 4: Get key details
if r3.ok and r3.json():
    key_id = r3.json()[0]['id']
    r4 = requests.get(f'http://localhost:8000/api/api-keys/{key_id}', headers=headers)
    print(f"4. Key details: {r4.status_code}")
    print(f"   Permissions: {r4.json()}")
EOF
```

- [ ] Run test script
- [ ] Check each test passes
- [ ] Fix issues as needed

### Contact Support

Include these details:
- [ ] API key format (tm_...)
- [ ] Error message
- [ ] Your request (curl command / code)
- [ ] Response code
- [ ] Response body
- [ ] When was key created
- [ ] When was it last used
- [ ] Any recent changes

---

## 📞 Getting Help

If none of these solutions work:

1. **Check Status Page**: `http://your-api/health`
2. **Review Logs**: Check application logs for errors
3. **Test with curl**: Isolate if issue is in code or API
4. **Contact Support**: Include the "Debugging Tips" above

---

**Is this not in the checklist?** See: `API_KEY_INTEGRATION_CHECKLIST.md`  
**Need more details?** See: `API_KEY_MANAGEMENT_GUIDE.md`  
**Quick reference?** See: `API_KEY_QUICK_START.md`
