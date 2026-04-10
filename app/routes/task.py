from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Task, User, TaskStatus
from app.schemas import (
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate,
    TaskMoveRequest,
    TaskWithDetails,
    TaskStatusEnum
)
from app.auth import get_current_active_user

router = APIRouter()


# Helper functions
def validate_user_exists(db: Session, user_id: int):
    """Validate that user exists"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with ID {user_id} does not exist"
        )
    return user


def get_max_position_in_status(db: Session, status_value: str) -> int:
    """Get the maximum position in a given status column"""
    max_pos = db.query(Task).filter(Task.status == status_value).order_by(Task.position.desc()).first()
    return max_pos.position if max_pos else -1


def reorder_positions(db: Session, status_value: str, start_position: int):
    """Reorder all positions after a given position in a status"""
    tasks = db.query(Task).filter(
        and_(Task.status == status_value, Task.position >= start_position)
    ).order_by(Task.position).all()
    
    for idx, task in enumerate(tasks):
        task.position = start_position + idx


# GET - List all tasks with filters
@router.get("", response_model=List[TaskSchema])
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatusEnum] = Query(None),
    assigned_to: Optional[int] = Query(None),
    created_by: Optional[int] = Query(None),
    overdue: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|due_date|priority|position)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with advanced filtering
    
    Query Parameters:
    - status: Filter by status (not_started, in_progress, completed)
    - assigned_to: Filter by assigned user ID
    - created_by: Filter by creator user ID
    - overdue: Filter overdue tasks (due_date < now and status != completed)
    - sort_by: Sort by field (created_at, due_date, priority, position)
    """
    query = db.query(Task)
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status.value)
    
    if assigned_to is not None:
        validate_user_exists(db, assigned_to)
        query = query.filter(Task.assigned_to == assigned_to)
    
    if created_by is not None:
        validate_user_exists(db, created_by)
        query = query.filter(Task.created_by == created_by)
    
    if overdue:
        query = query.filter(
            and_(
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatus.COMPLETED.value
            )
        )
    
    # Apply sorting
    if sort_by == "created_at":
        query = query.order_by(Task.created_at.desc())
    elif sort_by == "due_date":
        query = query.order_by(Task.due_date.desc())
    elif sort_by == "priority":
        query = query.order_by(Task.priority.desc())
    elif sort_by == "position":
        query = query.order_by(Task.status, Task.position)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


# POST - Create a new task
@router.post("", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task
    
    - assigned_to is optional; if provided, user must exist
    - New tasks start with status "not_started" and position at the end of the column
    """
    # Validate assigned user if provided
    if task.assigned_to is not None:
        validate_user_exists(db, task.assigned_to)
    
    # Get the next position for NOT_STARTED status
    next_position = get_max_position_in_status(db, TaskStatus.NOT_STARTED.value) + 1
    
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        created_by=current_user.id,
        status=TaskStatus.NOT_STARTED.value,
        position=next_position
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# GET - Get single task
@router.get("/{task_id}", response_model=TaskWithDetails)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get task by ID with creator and assignee details"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


# PUT - Update task details (not for status changes)
@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update task details (title, description, priority, due_date, assigned_to)
    
    Note: Use PATCH /tasks/{id}/move for changing status and position
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check authorization (creator or assignee can update)
    if db_task.created_by != current_user.id and db_task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    
    # If assigned_to is being changed, validate the user exists
    if "assigned_to" in update_data and update_data["assigned_to"] is not None:
        validate_user_exists(db, update_data["assigned_to"])
    
    for field, value in update_data.items():
        if field == "status" and value is not None:
            # Don't allow status changes here, use move endpoint instead
            continue
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# PATCH - Move task (change status and/or position)
@router.patch("/{task_id}/move", response_model=TaskSchema)
def move_task(
    task_id: int,
    move_request: TaskMoveRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Move task to a different status and/or position (Jira-like functionality)
    
    This endpoint handles:
    - Moving task between different status columns
    - Reordering task within the same column
    - Automatic position management in target column
    
    Example Request:
    {
        "new_status": "in_progress",
        "new_position": 2
    }
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check authorization (creator or assignee can move)
    if db_task.created_by != current_user.id and db_task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to move this task"
        )
    
    old_status = db_task.status
    old_position = db_task.position
    new_status = move_request.new_status.value
    new_position = move_request.new_position
    
    # If moving to completed status, set completed_at
    if new_status == TaskStatus.COMPLETED.value:
        db_task.completed_at = datetime.utcnow()
    else:
        db_task.completed_at = None
    
    # If changing status
    if old_status != new_status:
        # Reorder positions in old status (close the gap)
        reorder_positions(db, old_status, old_position + 1)
        
        # Reorder positions in new status to make room for this task
        reorder_positions(db, new_status, new_position)
        
        db_task.status = new_status
        db_task.position = new_position
    else:
        # Same status - just reorder
        if new_position < old_position:
            # Moving up - adjust positions between new and old
            tasks_to_shift = db.query(Task).filter(
                and_(
                    Task.status == old_status,
                    Task.position >= new_position,
                    Task.position < old_position
                )
            ).order_by(Task.position.desc()).all()
            
            for task in tasks_to_shift:
                task.position += 1
        elif new_position > old_position:
            # Moving down - adjust positions between old and new
            tasks_to_shift = db.query(Task).filter(
                and_(
                    Task.status == old_status,
                    Task.position > old_position,
                    Task.position <= new_position
                )
            ).order_by(Task.position).all()
            
            for task in tasks_to_shift:
                task.position -= 1
        
        db_task.position = new_position
    
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# DELETE - Delete task
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a task (only creator can delete)"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Only creator can delete
    if db_task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task creator can delete this task"
        )
    
    # Reorder remaining positions in this status
    old_status = db_task.status
    old_position = db_task.position
    
    db.delete(db_task)
    db.commit()
    
    # Close the gap in positions
    reorder_positions(db, old_status, old_position + 1)
    db.commit()
