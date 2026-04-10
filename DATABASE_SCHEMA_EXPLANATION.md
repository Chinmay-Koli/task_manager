# 📊 Database Schema Explanation

## Overview

The Task Manager API uses **SQLAlchemy ORM** with **SQLite** for development and **PostgreSQL** for production. The database schema consists of 4 main tables with relationships.

---

## Table Structure

### 1. **users** Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Purpose**: Store user account information
**Fields**:
- `id`: Unique user identifier (Primary Key)
- `username`: Login username (unique, required)
- `email`: User email (unique, required)
- `full_name`: User's full name
- `hashed_password`: Bcrypt-hashed password (never plaintext)
- `is_active`: Account activation status
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Relationships**:
- One User → Many Tasks (created)
- One User → Many Tasks (assigned)
- One User → Many API Keys

---

### 2. **tasks** Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'todo',
    priority INTEGER DEFAULT 3,
    created_by INTEGER NOT NULL FOREIGN KEY,
    assigned_to INTEGER FOREIGN KEY,
    position INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Purpose**: Store task/todo items

**Fields**:
- `id`: Unique task identifier (Primary Key)
- `title`: Task title (required)
- `description`: Detailed task description
- `status`: Task status ('todo', 'in_progress', 'completed', 'archived')
- `priority`: Task priority (1-5, with 3 as default)
- `created_by`: User ID who created task (Foreign Key → users.id)
- `assigned_to`: User ID assigned to task (Foreign Key → users.id, optional)
- `position`: Task order/position in list
- `created_at`: Task creation timestamp
- `updated_at`: Last modification timestamp

**Status Values**:
- `todo` - Not started
- `in_progress` - Currently being worked on
- `completed` - Finished
- `archived` - Archived/hidden

**Priority Levels**:
- 1: Low
- 2: Medium-Low
- 3: Medium (default)
- 4: Medium-High
- 5: High/Critical

**Relationships**:
- Many Tasks ← One User (created_by)
- Many Tasks ← One User (assigned_to)
- One Task → One API Key (for tracking)

---

### 3. **api_keys** Table (NEW)
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL FOREIGN KEY,
    name VARCHAR NOT NULL,
    hashed_key VARCHAR UNIQUE NOT NULL,
    prefix VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    can_read_tasks BOOLEAN DEFAULT TRUE,
    can_create_tasks BOOLEAN DEFAULT TRUE,
    can_update_tasks BOOLEAN DEFAULT TRUE,
    can_delete_tasks BOOLEAN DEFAULT FALSE,
    can_read_dashboard BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    expires_at DATETIME
)
```

**Purpose**: Store API keys for service-to-service authentication

**Fields**:
- `id`: Unique API key identifier (Primary Key)
- `user_id`: Owner user ID (Foreign Key → users.id)
- `name`: Friendly name for the key (e.g., "Mobile App", "CI/CD")
- `hashed_key`: SHA-256 hashed API key (never store plaintext!)
- `prefix`: First 8-10 characters for identification (e.g., "tm_a1b2c3")
- `is_active`: Whether key is active (disable without deleting)
- `can_read_tasks`: Permission to read tasks (boolean)
- `can_create_tasks`: Permission to create tasks (boolean)
- `can_update_tasks`: Permission to update tasks (boolean)
- `can_delete_tasks`: Permission to delete tasks (boolean)
- `can_read_dashboard`: Permission to access dashboard (boolean)
- `created_at`: Key creation timestamp
- `last_used_at`: Last time key was used (for auditing)
- `expires_at`: Optional expiration date (auto-revoke after)

**Permissions**:
- Granular control over what each API key can do
- Default: Read + Create + Update enabled, Delete disabled
- Used for authorization checks on each request

**Relationships**:
- Many API Keys ← One User

---

## ER Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ full_name       │
│ hashed_password │
│ is_active       │
│ created_at      │
└─────────────────┘
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
┌─────────────────┐     ┌──────────────────┐
│     tasks       │     │    api_keys      │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ title           │     │ user_id (FK)     │
│ description     │     │ name             │
│ status          │     │ hashed_key       │
│ priority        │     │ prefix           │
│ created_by (FK) ◄─────┤ is_active        │
│ assigned_to(FK) ◄─────┤ can_read_tasks   │
│ position        │     │ can_create_tasks │
│ created_at      │     │ can_update_tasks │
│ updated_at      │     │ can_delete_tasks │
└─────────────────┘     │ can_read_dashboard│
                        │ created_at       │
                        │ last_used_at     │
                        │ expires_at       │
                        └──────────────────┘
```

---

## Data Type Mappings

### SQLAlchemy to SQL

| SQLAlchemy Type | SQLite Type | PostgreSQL Type | Python Type |
|-----------------|-----------|-----------------|-----------|
| `Integer` | INTEGER | INTEGER | `int` |
| `String` | VARCHAR | VARCHAR | `str` |
| `Text` | TEXT | TEXT | `str` |
| `Boolean` | BOOLEAN | BOOLEAN | `bool` |
| `DateTime` | DATETIME | TIMESTAMP | `datetime` |
| `ForeignKey` | INTEGER | INTEGER | Reference |

---

## Indexes

**Performance Optimization** - Indexes created on frequently queried columns:

```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_prefix ON api_keys(prefix);
CREATE INDEX idx_api_keys_hashed_key ON api_keys(hashed_key);
```

**Why**:
- Speeds up WHERE clause queries
- Improves JOIN performance
- Accelerates sorting operations
- Reduces full table scans

---

## Constraints & Rules

### Primary Keys
- Every table has `id` as primary key (auto-increment)
- Guaranteed uniqueness for each record

### Foreign Keys
- `tasks.created_by` → `users.id` (required)
- `tasks.assigned_to` → `users.id` (optional)
- `api_keys.user_id` → `users.id` (required)
- Ensures referential integrity

### Unique Constraints
- `users.username` - No duplicate usernames
- `users.email` - No duplicate emails
- `api_keys.hashed_key` - No duplicate keys

### Default Values
- `tasks.status` = 'todo'
- `tasks.priority` = 3
- `api_keys.is_active` = True
- `api_keys.can_read_tasks` = True
- `api_keys.can_create_tasks` = True
- `api_keys.can_update_tasks` = True
- `api_keys.can_delete_tasks` = False
- `api_keys.can_read_dashboard` = True
- All `created_at` = Current Timestamp

### Not Null Constraints
- Users: `username`, `email`, `hashed_password`
- Tasks: `title`, `created_by`
- API Keys: `user_id`, `name`, `hashed_key`, `prefix`

---

## Data Relationships

### User to Tasks
```
1 User : N Tasks (created)
1 User : N Tasks (assigned)

Example:
User(1) creates Task(1), Task(2), Task(3)
User(1) is assigned to Task(2)
User(2) is assigned to Task(1), Task(3)
```

### User to API Keys
```
1 User : N API Keys

Example:
User(1) owns APIKey(1), APIKey(2), APIKey(3)
User(2) owns APIKey(4)
```

### Task Properties
```
Task(1):
  - created_by: User(1) - WHO created it
  - assigned_to: User(2) - WHO is working on it
  - status: 'in_progress' - WHERE it is
  - priority: 4 - HOW important
  - position: 1 - WHERE in list
```

---

## Security Considerations

### Password Storage
- Passwords NEVER stored in plaintext
- Bcrypt hashing with salt (passlib)
- Only ``hashed_password`` stored
- Cannot reverse-engineer password from hash

### API Key Storage
- API keys NEVER stored in plaintext
- SHA-256 hashing (one-way)
- Only `hashed_key` stored in database
- `prefix` field allows safe identification without exposing full key
- Keys shown only once on creation (`api_key` field returned only in response)

### Authentication Flow
```
User Password:
  plaintext → bcrypt hash → stored in DB
  
on login:
  input → bcrypt hash → compare with stored → match/no match

API Key:
  plaintext → SHA-256 hash → stored in DB
  
on request:
  input → SHA-256 hash → compare with stored → match/no match
```

---

## Database Initialization

### Automatic Creation (SQLAlchemy ORM)

When the API starts:

```python
from app.database import init_db

# This runs automatically on startup
init_db()  # Creates all tables if they don't exist
```

**Files Involved**:
- `app/models.py` - Defines table schemas
- `app/database.py` - Database connection & initialization
- `app/main.py` - Calls `init_db()` on start

### Manual Database Reset

```bash
# Delete database file (SQLite)
rm test.db

# On next API start, fresh database created automatically
python -m uvicorn app.main:app --reload
```

### PostgreSQL (Production)

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost/task_manager"

# Database must exist, tables auto-created
```

---

## Query Examples

### Create User
```python
from app.models import User
from app.database import get_db

user = User(
    username="john",
    email="john@example.com",
    full_name="John Doe",
    hashed_password="$2b$12$..."  # bcrypt hash
)
db.add(user)
db.commit()
```

### Create Task
```python
task = Task(
    title="Implement API",
    description="Build REST API endpoints",
    created_by=1,  # User ID
    assigned_to=2,  # Another User ID
    status="in_progress",
    priority=4
)
db.add(task)
db.commit()
```

### Find Tasks by User
```python
# Tasks created by user
created_tasks = db.query(Task).filter(Task.created_by == 1).all()

# Tasks assigned to user
assigned_tasks = db.query(Task).filter(Task.assigned_to == 1).all()

# Active tasks (not completed)
active_tasks = db.query(Task).filter(
    Task.status != "completed"
).all()
```

### Create API Key
```python
api_key = APIKey(
    user_id=1,
    name="Mobile App",
    hashed_key="abc123...",  # SHA-256 hash
    prefix="tm_abc123",
    can_read_tasks=True,
    can_create_tasks=True,
    can_update_tasks=True,
    can_delete_tasks=False,
    can_read_dashboard=True
)
db.add(api_key)
db.commit()
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Tables** | 4 (users, tasks, api_keys, + relationships) |
| **Total Fields** | ~30+ fields across all tables |
| **Primary Keys** | Auto-incrementing integers |
| **Foreign Keys** | 3 (tasks.created_by, tasks.assigned_to, api_keys.user_id) |
| **Unique Constraints** | 3 (users.username, users.email, api_keys.hashed_key) |
| **Indexed Columns** | 10 (for performance) |
| **Development DB** | SQLite (test.db) |
| **Production DB** | PostgreSQL |
| **No Migrations** | SQLAlchemy auto-creates schema |

---

## Related Files

- **Models**: [app/models.py](app/models.py)
- **Database Config**: [app/database.py](app/database.py)
- **Schemas**: [app/schemas.py](app/schemas.py)

---

**Database created**: April 10, 2026  
**Last updated**: April 10, 2026  
**Version**: 1.1.0 (with API Key Management)
