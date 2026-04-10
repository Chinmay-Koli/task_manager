from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Note: Relationships are defined in Task model with backref


class TaskStatus(str, enum.Enum):
    """Task status enumeration - Jira-compatible"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default=TaskStatus.NOT_STARTED.value, index=True)
    priority = Column(Integer, default=1)  # 1-5, higher is more important
    position = Column(Integer, default=0)  # Order within status column
    
    # User relationships
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who created the task
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who task is assigned to
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
