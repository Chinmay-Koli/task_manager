from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import APIKey, User
from app.schemas import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListItem,
    APIKeyUpdate,
    APIKeyRevoke
)
from app.auth import (
    get_current_active_user,
    generate_api_key,
    hash_api_key
)

router = APIRouter()


# ==================== API KEY ENDPOINTS ====================

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the current user.
    
    The full API key is shown only once. Store it securely.
    
    **Permissions:**
    - can_read_tasks: Can read tasks (default: true)
    - can_create_tasks: Can create new tasks (default: true)
    - can_update_tasks: Can update tasks (default: true)
    - can_delete_tasks: Can delete tasks (default: false)
    - can_read_dashboard: Can access dashboard (default: true)
    
    **Expiration:**
    - expires_in_days: Set to number of days before expiration (optional)
    - Leave blank for API key that never expires
    """
    # Generate new API key
    plain_key, prefix = generate_api_key()
    hashed_key = hash_api_key(plain_key)
    
    # Calculate expiration date if specified
    expires_at = None
    if api_key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
    
    # Create API key in database
    db_api_key = APIKey(
        user_id=current_user.id,
        name=api_key_data.name,
        hashed_key=hashed_key,
        prefix=prefix,
        expires_at=expires_at,
        can_read_tasks=api_key_data.can_read_tasks,
        can_create_tasks=api_key_data.can_create_tasks,
        can_update_tasks=api_key_data.can_update_tasks,
        can_delete_tasks=api_key_data.can_delete_tasks,
        can_read_dashboard=api_key_data.can_read_dashboard
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    # Return response with plain key (shown only once!)
    return APIKeyResponse(
        id=db_api_key.id,
        name=db_api_key.name,
        api_key=plain_key,  # Full key shown only here
        prefix=db_api_key.prefix,
        expires_at=db_api_key.expires_at,
        created_at=db_api_key.created_at
    )


@router.get("/api-keys", response_model=List[APIKeyListItem])
def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user.
    
    Note: Full API keys are not shown for security. Only the prefix is displayed.
    If you need the full key, you must create a new one.
    """
    db_api_keys = db.query(APIKey).filter(
        APIKey.user_id == current_user.id
    ).order_by(APIKey.created_at.desc()).all()
    
    return db_api_keys


@router.get("/api-keys/{api_key_id}", response_model=APIKeyListItem)
def get_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific API key.
    
    Only the API key owner can access key details.
    """
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return db_api_key


@router.patch("/api-keys/{api_key_id}", response_model=APIKeyListItem)
def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an API key's settings or permissions.
    
    You can:
    - Change the name
    - Enable/disable the key
    - Modify permissions
    """
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Update fields
    update_data = api_key_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            setattr(db_api_key, field, value)
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    api_key_id: int,
    revoke_request: APIKeyRevoke,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete/revoke an API key.
    
    This action cannot be undone. Any applications using this key will stop working.
    
    Require `confirm: true` in the request body to prevent accidental deletion.
    """
    if not revoke_request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm revocation by setting confirm: true"
        )
    
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(db_api_key)
    db.commit()
    
    # Return 204 No Content


@router.post("/api-keys/{api_key_id}/disable", response_model=APIKeyListItem)
def disable_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Temporarily disable an API key.
    
    The key still exists but cannot be used for authentication.
    Can be re-enabled later.
    """
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db_api_key.is_active = False
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key


@router.post("/api-keys/{api_key_id}/enable", response_model=APIKeyListItem)
def enable_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Re-enable a previously disabled API key.
    """
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db_api_key.is_active = True
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key


@router.get("/api-keys/{api_key_id}/usage")
def get_api_key_usage(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get usage information for an API key.
    """
    db_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {
        "id": db_api_key.id,
        "name": db_api_key.name,
        "prefix": db_api_key.prefix,
        "created_at": db_api_key.created_at,
        "last_used_at": db_api_key.last_used_at,
        "expires_at": db_api_key.expires_at,
        "is_active": db_api_key.is_active,
        "days_since_creation": (datetime.utcnow() - db_api_key.created_at).days if db_api_key.created_at else 0,
        "days_until_expiration": (db_api_key.expires_at - datetime.utcnow()).days if db_api_key.expires_at else None,
        "is_expired": db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow()
    }
