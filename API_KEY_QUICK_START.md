# 🔑 API KEY QUICK REFERENCE

## 5-Minute Setup

### Step 1: Create an API Key (via Postman)

1. **Import Postman collection** if not done yet
2. Go to **Authentication** → **Login User** → Send
3. Go to **API Keys** folder (new!) → **Create API Key**
4. Send the request with your desired permissions
5. Copy the `api_key` from response and save it! 🔒

### Step 2: Use API Key

Add this header to all requests:
```
X-API-Key: tm_your_api_key_here
```

Example in cURL:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_your_api_key_here"
```

### Step 3: Save It Securely

```bash
# Create .env file
echo "TASK_MANAGER_API_KEY=tm_your_api_key_here" > .env
```

---

## Copy-Paste Examples

### Create Task with API Key
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "description": "Task description",
    "priority": 3
  }'
```

### Get Tasks with API Key
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "X-API-Key: tm_your_key"
```

### Create API Key (via cURL)
```bash
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 90,
    "can_read_tasks": true,
    "can_create_tasks": true,
    "can_update_tasks": true,
    "can_delete_tasks": false,
    "can_read_dashboard": true
  }'
```

### List API Keys
```bash
curl -X GET http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Disable API Key
```bash
curl -X POST http://localhost:8000/api/api-keys/1/disable \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Delete API Key (Revoke)
```bash
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

---

## Postman Collection Updates

New **API Keys** folder added with endpoints:

- ✅ Create API Key
- ✅ List API Keys
- ✅ Get API Key
- ✅ Update API Key
- ✅ Disable API Key
- ✅ Enable API Key
- ✅ Delete API Key
- ✅ Get API Key Usage

**To Use in Postman**:
1. Re-import the collection (or reload)
2. Set `X-API-Key` header with value from "Create API Key" response
3. Use authenticated endpoints

---

## API Key Format

```
tm_[64-character-hex-string]

Example:
tm_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

Where:
- `tm_` = Task Manager prefix
- Rest = Random secure string

---

## Permissions Cheat Sheet

### Full Access (Use Carefully!)
```json
{
  "name": "Full Access",
  "can_read_tasks": true,
  "can_create_tasks": true,
  "can_update_tasks": true,
  "can_delete_tasks": true,
  "can_read_dashboard": true
}
```

### Read-Only (Safe)
```json
{
  "name": "Read Only",
  "can_read_tasks": true,
  "can_create_tasks": false,
  "can_update_tasks": false,
  "can_delete_tasks": false,
  "can_read_dashboard": true
}
```

### Create/Update Only
```json
{
  "name": "Bot User",
  "can_read_tasks": true,
  "can_create_tasks": true,
  "can_update_tasks": true,
  "can_delete_tasks": false,
  "can_read_dashboard": false
}
```

---

## Environment Variables Setup

### Windows (PowerShell)
```powershell
$env:TASK_MANAGER_API_KEY = "tm_your_key"
```

### Mac/Linux (Bash)
```bash
export TASK_MANAGER_API_KEY="tm_your_key"
```

### .env File
```
TASK_MANAGER_API_KEY=tm_your_key
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key
```

### Python Code
```python
import os

api_key = os.getenv('TASK_MANAGER_API_KEY')

headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/tasks', headers=headers)
```

### Node.js Code
```javascript
const apiKey = process.env.TASK_MANAGER_API_KEY;

const headers = {
  'X-API-Key': apiKey,
  'Content-Type': 'application/json'
};

fetch('http://localhost:8000/api/tasks', { headers })
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## All Endpoints

### API Key Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/api-keys` | Create key |
| GET | `/api/api-keys` | List keys |
| GET | `/api/api-keys/{id}` | Get key details |
| PATCH | `/api/api-keys/{id}` | Update key |
| DELETE | `/api/api-keys/{id}` | Delete key |
| POST | `/api/api-keys/{id}/disable` | Disable key |
| POST | `/api/api-keys/{id}/enable` | Enable key |
| GET | `/api/api-keys/{id}/usage` | View usage |

### With API Key Authentication
All existing endpoints now support API key auth:
- `GET/POST/PUT/DELETE /api/tasks`
- `GET /api/dashboard/stats`
- `GET /api/dashboard/team-stats`
- etc.

---

## Security Checklist

- [ ] Created initial API key
- [ ] Saved key to secure location (.env file)
- [ ] Added to `.gitignore` if in repo
- [ ] Set expiration date (e.g., 90 days)
- [ ] Restricted permissions (don't enable delete if not needed)
- [ ] Not sharing key via email/chat/public
- [ ] Planning key rotation schedule
- [ ] Know how to revoke key if leaked

---

## Common Tasks

### "I want to use API key in my app"

1. Create API key: `POST /api/api-keys`
2. Save to `.env` file
3. Load in code: `api_key = os.getenv('TASK_MANAGER_API_KEY')`
4. Use in header: `X-API-Key: {api_key}`

### "I need a read-only API key"

Create with:
```json
{
  "name": "Dashboard Reader",
  "can_read_tasks": true,
  "can_create_tasks": false,
  "can_update_tasks": false,
  "can_delete_tasks": false,
  "can_read_dashboard": true
}
```

### "My key is compromised!"

1. Immediately delete: `DELETE /api/api-keys/{id}`
2. Create new key
3. Update all applications
4. Review logs for unauthorized access

### "How do I test API key locally?"

```bash
# 1. Create key (get full key from response)
# 2. Set locally
export TASK_MANAGER_API_KEY="tm_..."

# 3. Test
curl -H "X-API-Key: $TASK_MANAGER_API_KEY" \
  http://localhost:8000/api/tasks
```

### "Rotate API keys every 90 days"

```bash
# 1. Create new key
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"name": "Rotated 2026-04", "expires_in_days": 90}'

# 2. Save new key to .env

# 3. Update app to use new key

# 4. Delete old key
curl -X DELETE http://localhost:8000/api/api-keys/1 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"confirm": true}'
```

---

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid API key" | Key doesn't exist | Check key is correct |
| "API key is inactive" | Key disabled | Enable key or create new one |
| "API key has expired" | Expiration date passed | Create new key |
| "Permission denied" | Key lacks permission | Update permissions or new key |
| "Not authenticated" | Missing X-API-Key header | Add header to request |

---

## Quick Stats

✅ **Supports**:
- Unlimited API keys per user
- Custom expiration (1-365 days)
- Granular permissions (5 types)
- Usage tracking (last used time)
- Key disabling/enabling
- Key rotation

✅ **Security**:
- SHA-256 hashing (keys not stored in plaintext)
- Unique key per creation
- Prefix identification
- Expiration enforcement
- Permission validation

✅ **Integrations**:
- Third-party apps
- Automation tools
- CI/CD pipelines
- Bots & scripts
- Mobile apps

---

## Need Help?

1. **Full Guide**: See `API_KEY_MANAGEMENT_GUIDE.md`
2. **Postman Collection**: Pre-configured in collection
3. **Live Docs**: Visit `/docs` at http://localhost:8000/docs
4. **Examples**: Check examples section in full guide

---

**Start using API keys now for secure integrations!** 🚀
