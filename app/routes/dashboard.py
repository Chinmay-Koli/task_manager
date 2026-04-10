from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Task, User, TaskStatus
from app.auth import get_current_active_user
from app.schemas import User as UserSchema

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user (personal)"""
    # Tasks assigned to or created by current user
    user_tasks = db.query(Task).filter(
        (Task.assigned_to == current_user.id) | (Task.created_by == current_user.id)
    )
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(Task.status == TaskStatus.COMPLETED.value).count()
    not_started_tasks = user_tasks.filter(Task.status == TaskStatus.NOT_STARTED.value).count()
    in_progress_tasks = user_tasks.filter(Task.status == TaskStatus.IN_PROGRESS.value).count()
    
    # High priority tasks count
    high_priority_tasks = user_tasks.filter(Task.priority >= 4).count()
    
    # Overdue tasks
    overdue_tasks = user_tasks.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != TaskStatus.COMPLETED.value
    ).count()
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "not_started_tasks": not_started_tasks,
        "in_progress_tasks": in_progress_tasks,
        "high_priority_tasks": high_priority_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "user_id": current_user.id
    }


@router.get("/team-stats")
def get_team_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get team-wide dashboard statistics"""
    all_tasks = db.query(Task)
    
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(Task.status == TaskStatus.COMPLETED.value).count()
    not_started_tasks = all_tasks.filter(Task.status == TaskStatus.NOT_STARTED.value).count()
    in_progress_tasks = all_tasks.filter(Task.status == TaskStatus.IN_PROGRESS.value).count()
    
    # High priority tasks count
    high_priority_tasks = all_tasks.filter(Task.priority >= 4).count()
    
    # Overdue tasks
    overdue_tasks = all_tasks.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != TaskStatus.COMPLETED.value
    ).count()
    
    # Tasks by user
    tasks_by_user = db.query(User.id, User.username, func.count(Task.id).label("task_count")).join(
        Task, (Task.assigned_to == User.id) | (Task.created_by == User.id), isouter=True
    ).group_by(User.id, User.username).all()
    
    user_stats = [
        {
            "user_id": user_id,
            "username": username,
            "task_count": task_count or 0
        }
        for user_id, username, task_count in tasks_by_user
    ]
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "not_started_tasks": not_started_tasks,
        "in_progress_tasks": in_progress_tasks,
        "high_priority_tasks": high_priority_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "tasks_by_user": user_stats
    }


@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for current user"""
    # Tasks assigned to or created by current user
    user_tasks = db.query(Task).filter(
        (Task.assigned_to == current_user.id) | (Task.created_by == current_user.id)
    )
    
    # Get recent tasks (last 5)
    recent_tasks = user_tasks.order_by(Task.created_at.desc()).limit(5).all()
    
    # Get upcoming tasks (due soon)
    upcoming_tasks = user_tasks.filter(
        Task.due_date != None,
        Task.due_date <= datetime.utcnow() + timedelta(days=7),
        Task.status != TaskStatus.COMPLETED.value
    ).order_by(Task.due_date).limit(5).all()
    
    # Get overdue tasks
    overdue_tasks = user_tasks.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != TaskStatus.COMPLETED.value
    ).order_by(Task.due_date).limit(5).all()
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        },
        "recent_tasks": recent_tasks,
        "upcoming_tasks": upcoming_tasks,
        "overdue_tasks": overdue_tasks
    }


@router.get("/user/{user_id}/workload")
def get_user_workload(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get workload for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_tasks = db.query(Task).filter(
        (Task.assigned_to == user_id) | (Task.created_by == user_id)
    )
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(Task.status == TaskStatus.COMPLETED.value).count()
    in_progress_tasks = user_tasks.filter(Task.status == TaskStatus.IN_PROGRESS.value).count()
    not_started_tasks = user_tasks.filter(Task.status == TaskStatus.NOT_STARTED.value).count()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        },
        "workload": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "not_started_tasks": not_started_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    }
