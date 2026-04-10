from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Task Status Enum
class TaskStatusEnum(str, Enum):
    """Allowed task statuses"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithTasks(User):
    """User with tasks schema"""
    created_tasks: List["Task"] = []
    assigned_tasks: List["Task"] = []


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: int = Field(1, ge=1, le=5)
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty"""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class TaskCreate(TaskBase):
    """Task creation schema"""
    pass


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None


class TaskMoveRequest(BaseModel):
    """Request body for moving tasks between columns"""
    new_status: TaskStatusEnum
    new_position: int = Field(0, ge=0)


class Task(TaskBase):
    """Task response schema"""
    id: int
    created_by: int
    assigned_to: Optional[int]
    status: str
    position: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskWithDetails(Task):
    """Task with creator and assignee details"""
    creator: Optional[User] = None
    assignee: Optional[User] = None


# Token Schemas
class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


# ==================== API KEY SCHEMAS ====================

class APIKeyCreate(BaseModel):
    """Schema for creating a new API key"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)  # None = never expires
    
    # Permissions (can restrict access)
    can_read_tasks: bool = True
    can_create_tasks: bool = True
    can_update_tasks: bool = True
    can_delete_tasks: bool = False
    can_read_dashboard: bool = True


class APIKeyResponse(BaseModel):
    """Schema for API key response (shown only once when created)"""
    id: int
    name: str
    api_key: str  # Full key shown only when created
    prefix: str  # First 10 chars for identification
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyListItem(BaseModel):
    """Schema for listing API keys (key hidden for security)"""
    id: int
    name: str
    prefix: str  # Only show prefix for security
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    # Permissions summary
    can_read_tasks: bool
    can_create_tasks: bool
    can_update_tasks: bool
    can_delete_tasks: bool
    can_read_dashboard: bool
    
    class Config:
        from_attributes = True


class APIKeyUpdate(BaseModel):
    """Schema for updating API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    
    # Permissions updates
    can_read_tasks: Optional[bool] = None
    can_create_tasks: Optional[bool] = None
    can_update_tasks: Optional[bool] = None
    can_delete_tasks: Optional[bool] = None
    can_read_dashboard: Optional[bool] = None


class APIKeyRevoke(BaseModel):
    """Schema for revoking/deleting API key"""
    confirm: bool = Field(..., description="Set to true to confirm revocation")
