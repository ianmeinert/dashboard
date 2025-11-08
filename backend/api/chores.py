"""
Chores API Router

This module provides REST API endpoints for managing chores, completions, and family member points
using async SQLAlchemy and SQLite. Part of the Family Dashboard project.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from ..core.exceptions import (DatabaseException, NotFoundException,
                               ValidationException)
from ..database import get_db
from ..models import (
    Chore, ChoreCompletion, AgeGroup, FamilyMember,
    WeeklyPointsArchive, MonthlyPointsArchive
)
from ..schemas.chores import (
    ChoreStatus, RecurrencePattern, ChoreCategory, ChorePriority,
    ChoreCreate, ChoreUpdate, ChoreResponse,
    ChoreCompletionCreate, ChoreCompletionResponse,
    FamilyMemberPointsResponse, FamilyMemberCreate, FamilyMemberUpdate,
    AgeGroupResponse, AgeGroupCreate, AgeGroupUpdate,
    ChoreListResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router with explicit prefix
chores_router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_weekly_cap(member: FamilyMember, points: int) -> bool:
    """Check if member can earn more points without exceeding weekly cap"""
    return (member.weekly_points + points) <= member.weekly_points_cap


def calculate_next_due_date(chore: Chore, from_date: Optional[datetime] = None) -> Optional[datetime]:
    """Calculate next due date based on recurrence
    
    Args:
        chore: The chore to calculate for
        from_date: Optional date to calculate from (defaults to chore.due_date)
    
    Returns:
        Next due date or None if not recurring
    """
    if not chore.recurrence_type or not chore.recurrence_interval:
        return chore.due_date
    
    base_date = from_date if from_date else (chore.due_date or datetime.utcnow())
    
    if chore.recurrence_type == RecurrencePattern.DAILY:
        return base_date + timedelta(days=chore.recurrence_interval)
    elif chore.recurrence_type == RecurrencePattern.WEEKLY:
        return base_date + timedelta(weeks=chore.recurrence_interval)
    elif chore.recurrence_type == RecurrencePattern.BIWEEKLY:
        return base_date + timedelta(weeks=2 * chore.recurrence_interval)
    elif chore.recurrence_type == RecurrencePattern.MONTHLY:
        # Approximate month as 30 days
        return base_date + timedelta(days=30 * chore.recurrence_interval)
    
    return None


async def reset_weekly_points(db: AsyncSession):
    """Reset weekly points for all members (call from scheduled task)"""
    try:
        result = await db.execute(select(FamilyMember))
        members = result.scalars().all()
        
        for member in members:
            # Archive current weekly points
            archive = WeeklyPointsArchive(
                family_member_id=member.id,
                points_earned=member.weekly_points,
                week_start_date=member.last_weekly_reset,
                week_end_date=datetime.utcnow()
            )
            db.add(archive)
            
            # Reset weekly points
            member.weekly_points = 0
            member.last_weekly_reset = datetime.utcnow()
        
        await db.commit()
        logger.info(f"Reset weekly points for {len(members)} family members")
    except Exception as e:
        logger.error(f"Error resetting weekly points: {e}", exc_info=True)
        raise DatabaseException("Failed to reset weekly points", operation="update")


async def reset_monthly_points(db: AsyncSession):
    """Reset monthly points for all members (call from scheduled task)"""
    try:
        result = await db.execute(select(FamilyMember))
        members = result.scalars().all()
        
        for member in members:
            # Archive current monthly points
            archive = MonthlyPointsArchive(
                family_member_id=member.id,
                points_earned=member.monthly_points,
                month_start_date=member.last_monthly_reset,
                month_end_date=datetime.utcnow()
            )
            db.add(archive)
            
            # Reset monthly points
            member.monthly_points = 0
            member.last_monthly_reset = datetime.utcnow()
        
        await db.commit()
        logger.info(f"Reset monthly points for {len(members)} family members")
    except Exception as e:
        logger.error(f"Error resetting monthly points: {e}", exc_info=True)
        raise DatabaseException("Failed to reset monthly points", operation="update")


# ============================================================================
# AGE GROUP ENDPOINTS (Must come BEFORE parametric routes)
# ============================================================================

@chores_router.get("/age-groups", response_model=List[AgeGroupResponse])
async def get_age_groups(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> List[AgeGroupResponse]:
    """
    Get all age groups and their weekly point caps.
    """
    try:
        result = await db.execute(select(AgeGroup))
        age_groups = result.scalars().all()
        
        return [AgeGroupResponse.model_validate(ag) for ag in age_groups]
    except Exception as e:
        logger.error(f"Error getting age groups: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve age groups", operation="select")


@chores_router.post("/age-groups", response_model=AgeGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_age_group(
    request: Request,
    age_group: AgeGroupCreate,
    db: AsyncSession = Depends(get_db)
) -> AgeGroupResponse:
    """
    Create a new age group.
    """
    try:
        # Validate input
        if not age_group.name or not age_group.name.strip():
            raise ValidationException("Age group name is required")
        
        if age_group.min_age > age_group.max_age:
            raise ValidationException("Minimum age cannot be greater than maximum age")
        
        # Check for duplicate name
        existing_result = await db.execute(
            select(AgeGroup).where(AgeGroup.name == age_group.name.strip())
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise ValidationException(f"Age group '{age_group.name}' already exists")
        
        now = datetime.utcnow()
        db_age_group = AgeGroup(
            name=age_group.name.strip(),
            min_age=age_group.min_age,
            max_age=age_group.max_age,
            default_weekly_cap=age_group.default_weekly_cap,
            created_at=now,
            updated_at=now
        )
        
        db.add(db_age_group)
        await db.commit()
        await db.refresh(db_age_group)
        
        return AgeGroupResponse.model_validate(db_age_group)
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error creating age group: {e}", exc_info=True)
        raise DatabaseException("Failed to create age group", operation="insert")


@chores_router.get("/age-groups/{age_group_id}", response_model=AgeGroupResponse)
async def get_age_group(
    request: Request,
    age_group_id: int,
    db: AsyncSession = Depends(get_db)
) -> AgeGroupResponse:
    """
    Get a specific age group by ID.
    """
    try:
        result = await db.execute(select(AgeGroup).where(AgeGroup.id == age_group_id))
        age_group = result.scalar_one_or_none()
        
        if not age_group:
            raise NotFoundException("Age group", str(age_group_id))
        
        return AgeGroupResponse.model_validate(age_group)
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting age group {age_group_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve age group", operation="select")


@chores_router.put("/age-groups/{age_group_id}", response_model=AgeGroupResponse)
async def update_age_group(
    request: Request,
    age_group_id: int,
    age_group_update: AgeGroupUpdate,
    db: AsyncSession = Depends(get_db)
) -> AgeGroupResponse:
    """
    Update an existing age group.
    """
    try:
        result = await db.execute(select(AgeGroup).where(AgeGroup.id == age_group_id))
        age_group = result.scalar_one_or_none()
        
        if not age_group:
            raise NotFoundException("Age group", str(age_group_id))
        
        # Update fields
        update_data = age_group_update.model_dump(exclude_unset=True)
        
        # Validate age range if both are being updated
        min_age = update_data.get('min_age', age_group.min_age)
        max_age = update_data.get('max_age', age_group.max_age)
        if min_age > max_age:
            raise ValidationException("Minimum age cannot be greater than maximum age")
        
        for field, value in update_data.items():
            setattr(age_group, field, value)
        
        age_group.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(age_group)
        
        return AgeGroupResponse.model_validate(age_group)
    except (NotFoundException, ValidationException):
        await db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error updating age group {age_group_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to update age group", operation="update")


@chores_router.delete("/age-groups/{age_group_id}")
async def delete_age_group(
    request: Request,
    age_group_id: int,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Delete an age group. Cannot delete if family members are assigned to it.
    """
    try:
        result = await db.execute(select(AgeGroup).where(AgeGroup.id == age_group_id))
        age_group = result.scalar_one_or_none()
        
        if not age_group:
            raise NotFoundException("Age group", str(age_group_id))
        
        # Check if any family members are using this age group
        members_result = await db.execute(
            select(FamilyMember).where(FamilyMember.age_group_id == age_group_id)
        )
        members = members_result.scalars().all()
        
        if members:
            member_names = ", ".join([m.name for m in members])
            raise ValidationException(
                f"Cannot delete age group. It is assigned to: {member_names}"
            )
        
        await db.delete(age_group)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Age group with ID {age_group_id} deleted successfully"}
        )
    except (NotFoundException, ValidationException):
        await db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error deleting age group {age_group_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to delete age group", operation="delete")


# ============================================================================
# FAMILY MEMBER ENDPOINTS (Must come BEFORE parametric routes)
# ============================================================================

@chores_router.get("/members", response_model=List[FamilyMemberPointsResponse])
async def get_family_members(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> List[FamilyMemberPointsResponse]:
    """
    Get all family members with their current points status.
    """
    try:
        result = await db.execute(select(FamilyMember))
        members = result.scalars().all()
        
        responses = []
        for member in members:
            weekly_remaining = member.weekly_points_cap - member.weekly_points
            progress_percent = (member.weekly_points / member.weekly_points_cap * 100) if member.weekly_points_cap > 0 else 0
            
            # Get age group name
            age_group_result = await db.execute(
                select(AgeGroup).where(AgeGroup.id == member.age_group_id)
            )
            age_group = age_group_result.scalar_one_or_none()
            
            response = FamilyMemberPointsResponse(
                id=member.id,
                name=member.name,
                age=member.age,
                age_group_id=member.age_group_id,
                is_active=member.is_active,
                age_group_name=age_group.name if age_group else "Unknown",
                total_points=member.total_points,
                weekly_points=member.weekly_points,
                weekly_points_cap=member.weekly_points_cap,
                weekly_points_remaining=weekly_remaining,
                weekly_progress_percent=round(progress_percent, 1),
                monthly_points=member.monthly_points,
                last_weekly_reset=member.last_weekly_reset,
                last_monthly_reset=member.last_monthly_reset,
                created_at=member.created_at,
                updated_at=member.updated_at,
                age_group=None  # Optional, can be included if needed
            )
            responses.append(response)
        
        return responses
    except Exception as e:
        logger.error(f"Error getting family members: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve family members", operation="select")


@chores_router.post("/members", response_model=FamilyMemberPointsResponse, status_code=status.HTTP_201_CREATED)
async def create_family_member(
    request: Request,
    member: FamilyMemberCreate,
    db: AsyncSession = Depends(get_db)
) -> FamilyMemberPointsResponse:
    """
    Create a new family member.
    """
    try:
        # Validate input
        if not member.name or not member.name.strip():
            raise ValidationException("Family member name is required")
        
        # Verify age group exists if provided
        age_group = None
        if member.age_group_id:
            age_group_result = await db.execute(
                select(AgeGroup).where(AgeGroup.id == member.age_group_id)
            )
            age_group = age_group_result.scalar_one_or_none()
            if not age_group:
                raise NotFoundException("Age group", str(member.age_group_id))
        
        now = datetime.utcnow()
        
        # Get weekly cap from age group or use default
        weekly_cap = age_group.default_weekly_cap if age_group else 25
        
        db_member = FamilyMember(
            name=member.name.strip(),
            age=member.age,
            age_group_id=member.age_group_id,
            is_active=member.is_active if hasattr(member, 'is_active') else True,
            total_points=0,
            weekly_points=0,
            monthly_points=0,
            weekly_points_cap=weekly_cap,
            last_weekly_reset=now,
            last_monthly_reset=now,
            created_at=now,
            updated_at=now
        )
        
        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)
        
        # Build response
        return FamilyMemberPointsResponse(
            id=db_member.id,
            name=db_member.name,
            age=db_member.age,
            age_group_id=db_member.age_group_id,
            is_active=db_member.is_active,
            age_group_name=age_group.name if age_group else "Unknown",
            total_points=db_member.total_points,
            weekly_points=db_member.weekly_points,
            weekly_points_cap=db_member.weekly_points_cap,
            weekly_points_remaining=db_member.weekly_points_cap,
            weekly_progress_percent=0.0,
            monthly_points=db_member.monthly_points,
            last_weekly_reset=db_member.last_weekly_reset,
            last_monthly_reset=db_member.last_monthly_reset,
            created_at=db_member.created_at,  # ADD THIS
            updated_at=db_member.updated_at   # ADD THIS
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"Error creating family member: {e}", exc_info=True)
        raise DatabaseException("Failed to create family member", operation="insert")


@chores_router.get("/members/{member_id}", response_model=FamilyMemberPointsResponse)
async def get_family_member(
    request: Request,
    member_id: int,
    db: AsyncSession = Depends(get_db)
) -> FamilyMemberPointsResponse:
    """
    Get a specific family member's points status.
    """
    try:
        result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundException("Family member", str(member_id))
        
        weekly_remaining = member.weekly_points_cap - member.weekly_points
        progress_percent = (member.weekly_points / member.weekly_points_cap * 100) if member.weekly_points_cap > 0 else 0
        
        # Get age group name
        age_group_result = await db.execute(
            select(AgeGroup).where(AgeGroup.id == member.age_group_id)
        )
        age_group = age_group_result.scalar_one_or_none()
        
        return FamilyMemberPointsResponse(
            id=member.id,
            name=member.name,
            age=member.age,
            age_group_id=member.age_group_id,
            is_active=member.is_active,
            age_group_name=age_group.name if age_group else "Unknown",
            total_points=member.total_points,
            weekly_points=member.weekly_points,
            weekly_points_cap=member.weekly_points_cap,
            weekly_points_remaining=weekly_remaining,
            weekly_progress_percent=round(progress_percent, 1),
            monthly_points=member.monthly_points,
            last_weekly_reset=member.last_weekly_reset,
            last_monthly_reset=member.last_monthly_reset,
            created_at=member.created_at,
            updated_at=member.updated_at
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting family member {member_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve family member", operation="select")


@chores_router.put("/members/{member_id}", response_model=FamilyMemberPointsResponse)
async def update_family_member(
    request: Request,
    member_id: int,
    member_update: FamilyMemberUpdate,
    db: AsyncSession = Depends(get_db)
) -> FamilyMemberPointsResponse:
    """
    Update an existing family member.
    """
    try:
        result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundException("Family member", str(member_id))
        
        # Verify age group exists if updating
        update_data = member_update.model_dump(exclude_unset=True)
        if "age_group_id" in update_data and update_data["age_group_id"]:
            age_group_result = await db.execute(
                select(AgeGroup).where(AgeGroup.id == update_data["age_group_id"])
            )
            age_group = age_group_result.scalar_one_or_none()
            if not age_group:
                raise NotFoundException("Age group", str(update_data["age_group_id"]))
        
        # Update fields
        for field, value in update_data.items():
            setattr(member, field, value)
        
        member.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(member)
        
        # Build response
        weekly_remaining = member.weekly_points_cap - member.weekly_points
        progress_percent = (member.weekly_points / member.weekly_points_cap * 100) if member.weekly_points_cap > 0 else 0
        
        age_group_result = await db.execute(
            select(AgeGroup).where(AgeGroup.id == member.age_group_id)
        )
        age_group = age_group_result.scalar_one_or_none()
        
        return FamilyMemberPointsResponse(
            id=member.id,
            name=member.name,
            age=member.age,
            age_group_id=member.age_group_id,
            is_active=member.is_active,
            age_group_name=age_group.name if age_group else "Unknown",
            total_points=member.total_points,
            weekly_points=member.weekly_points,
            weekly_points_cap=member.weekly_points_cap,
            weekly_points_remaining=weekly_remaining,
            weekly_progress_percent=round(progress_percent, 1),
            monthly_points=member.monthly_points,
            last_weekly_reset=member.last_weekly_reset,
            last_monthly_reset=member.last_monthly_reset,
            created_at=member.created_at,
            updated_at=member.updated_at
        )
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        logger.error(f"Error updating family member {member_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to update family member", operation="update")


@chores_router.delete("/members/{member_id}")
async def delete_family_member(
    request: Request,
    member_id: int,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Delete a family member. Cannot delete if they have assigned chores or completions.
    """
    try:
        result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundException("Family member", str(member_id))
        
        # Check for assigned chores
        chores_result = await db.execute(
            select(Chore).where(Chore.assigned_to_id == member_id)
        )
        assigned_chores = chores_result.scalars().all()
        
        if assigned_chores:
            raise ValidationException(
                f"Cannot delete family member. They have {len(assigned_chores)} assigned chore(s)"
            )
        
        # Check for completion history
        completions_result = await db.execute(
            select(ChoreCompletion).where(ChoreCompletion.completed_by_id == member_id)
        )
        completions = completions_result.scalars().all()
        
        if completions:
            raise ValidationException(
                f"Cannot delete family member. They have {len(completions)} completion record(s)"
            )
        
        await db.delete(member)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Family member with ID {member_id} deleted successfully"}
        )
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        logger.error(f"Error deleting family member {member_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to delete family member", operation="delete")


# ============================================================================
# CHORE COMPLETION ENDPOINTS (Must come BEFORE parametric routes)
# ============================================================================

@chores_router.get("/completions", response_model=List[ChoreCompletionResponse])
async def get_completions(
    request: Request,
    completed_by_id: Optional[int] = None,
    chore_id: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> List[ChoreCompletionResponse]:
    """
    Get chore completion history with optional filtering.
    """
    try:
        stmt = select(ChoreCompletion).order_by(ChoreCompletion.completed_at.desc())
        
        if completed_by_id:
            stmt = stmt.where(ChoreCompletion.completed_by_id == completed_by_id)
        
        if chore_id:
            stmt = stmt.where(ChoreCompletion.chore_id == chore_id)
        
        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        completions = result.scalars().all()
        
        # Add member names
        responses = []
        for completion in completions:
            response_dict = ChoreCompletionResponse.model_validate(completion).model_dump()
            
            member_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == completion.completed_by_id)
            )
            member = member_result.scalar_one_or_none()
            response_dict['completed_by_name'] = member.name if member else "Unknown"
            
            responses.append(response_dict)
        
        return responses
    except Exception as e:
        logger.error(f"Error getting completions: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve completions", operation="select")


@chores_router.post("/completions", response_model=ChoreCompletionResponse, status_code=status.HTTP_201_CREATED)
async def complete_chore(
    request: Request,
    completion: ChoreCompletionCreate,
    db: AsyncSession = Depends(get_db)
) -> ChoreCompletionResponse:
    """
    Mark a chore as completed and award points.
    """
    try:
        # Get chore
        chore_result = await db.execute(select(Chore).where(Chore.id == completion.chore_id))
        chore = chore_result.scalar_one_or_none()
        if not chore:
            raise NotFoundException("Chore", str(completion.chore_id))
        
        # Get family member
        member_result = await db.execute(
            select(FamilyMember).where(FamilyMember.id == completion.completed_by_id)
        )
        member = member_result.scalar_one_or_none()
        if not member:
            raise NotFoundException("Family member", str(completion.completed_by_id))
        
        # Prevent completing chores before their due date
        now = datetime.utcnow()
        if chore.due_date:
            today = now.date()
            if chore.due_date > today:
                # Format the date properly
                due_date_str = chore.due_date.strftime('%Y-%m-%d') if hasattr(chore.due_date, 'strftime') else str(chore.due_date)
                logger.info(f"Chore completion blocked: chore {chore.id} not due until {due_date_str}")
                # Explicitly rollback before raising exception
                await db.rollback()
                raise ValidationException(
                    f"This chore is not due until {due_date_str}. "
                    f"You can complete it on or after the due date."
                )
        
        # Check weekly cap
        if not check_weekly_cap(member, chore.points):
            remaining = member.weekly_points_cap - member.weekly_points
            # Explicitly rollback before raising exception
            await db.rollback()
            raise ValidationException(
                f"Weekly points cap exceeded. Remaining: {remaining} points"
            )
        
        now = datetime.utcnow()
        
        # Create completion record
        db_completion = ChoreCompletion(
            chore_id=chore.id,
            chore_title_snapshot=chore.title,
            completed_by_id=member.id,
            points_earned=chore.points,
            completed_at=now,
            completion_notes=completion.completion_notes,
            actual_minutes=completion.actual_minutes,
            photo_url=completion.photo_url
        )
        db.add(db_completion)
        
        # Award points to member
        member.total_points += chore.points
        member.weekly_points += chore.points
        member.monthly_points += chore.points
        
        # Update chore status
        chore.status = ChoreStatus.COMPLETED
        chore.completed_at = now  # Set completion timestamp for Option B filtering
        
        # Handle recurring chores (but not if recurrence type is "none")
        if chore.recurrence_type and chore.recurrence_type != RecurrencePattern.NONE and chore.recurrence_interval:
            # Archive the completed recurring chore (so it doesn't clutter the list)
            chore.is_archived = True
            
            # Calculate next due date from today if past due, otherwise from original due date
            today = now.date()
            base_date = today if chore.due_date < today else chore.due_date
            
            # Calculate next occurrence
            if chore.recurrence_type == RecurrencePattern.DAILY:
                next_due = base_date + timedelta(days=chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.WEEKLY:
                next_due = base_date + timedelta(weeks=chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.BIWEEKLY:
                next_due = base_date + timedelta(weeks=2 * chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.MONTHLY:
                month = base_date.month + chore.recurrence_interval
                year = base_date.year
                while month > 12:
                    month -= 12
                    year += 1
                next_due = base_date.replace(year=year, month=month)
            else:
                next_due = base_date
            
            # Calculate the next occurrence after that
            if chore.recurrence_type == RecurrencePattern.DAILY:
                next_next_due = next_due + timedelta(days=chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.WEEKLY:
                next_next_due = next_due + timedelta(weeks=chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.BIWEEKLY:
                next_next_due = next_due + timedelta(weeks=2 * chore.recurrence_interval)
            elif chore.recurrence_type == RecurrencePattern.MONTHLY:
                month = next_due.month + chore.recurrence_interval
                year = next_due.year
                while month > 12:
                    month -= 12
                    year += 1
                next_next_due = next_due.replace(year=year, month=month)
            else:
                next_next_due = next_due
            
            # Create new chore for next occurrence
            new_chore = Chore(
                title=chore.title,
                description=chore.description,
                points=chore.points,
                category=chore.category,
                priority=chore.priority,
                assigned_to_id=chore.assigned_to_id,
                created_by_id=chore.created_by_id,
                status=ChoreStatus.PENDING,
                due_date=next_due,
                recurrence_type=chore.recurrence_type,
                recurrence_interval=chore.recurrence_interval,
                next_due_date=next_next_due,
                notes=chore.notes,
                estimated_minutes=chore.estimated_minutes
            )
            db.add(new_chore)
        
        await db.commit()
        await db.refresh(db_completion)
        
        # Build response
        response_dict = ChoreCompletionResponse.model_validate(db_completion).model_dump()
        response_dict['completed_by_name'] = member.name
        
        logger.info(
            f"Chore '{chore.title}' completed by {member.name}. "
            f"Earned {chore.points} points. "
            f"Weekly total: {member.weekly_points}/{member.weekly_points_cap}"
        )
        
        return ChoreCompletionResponse(**response_dict)
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        logger.error(f"Error completing chore: {e}", exc_info=True)
        raise DatabaseException("Failed to complete chore", operation="insert")


# ============================================================================
# ADMIN ENDPOINTS (Must come BEFORE parametric routes)
# ============================================================================

@chores_router.get("/dashboard")
async def get_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get dashboard summary with all key metrics.
    """
    try:
        # Update overdue status before calculating metrics
        from backend.services.chores import ChoreService
        await ChoreService.update_overdue_status(db)
        # Get all members with their points
        members_result = await db.execute(select(FamilyMember))
        members = members_result.scalars().all()
        
        members_data = []
        for member in members:
            weekly_remaining = member.weekly_points_cap - member.weekly_points
            progress_percent = (member.weekly_points / member.weekly_points_cap * 100) if member.weekly_points_cap > 0 else 0
            
            age_group_result = await db.execute(
                select(AgeGroup).where(AgeGroup.id == member.age_group_id)
            )
            age_group = age_group_result.scalar_one_or_none()
            
            members_data.append({
                "id": member.id,
                "name": member.name,
                "age_group_name": age_group.name if age_group else "Unknown",
                "total_points": member.total_points,
                "weekly_points": member.weekly_points,
                "weekly_points_cap": member.weekly_points_cap,
                "weekly_points_remaining": weekly_remaining,
                "weekly_progress_percent": round(progress_percent, 1),
                "monthly_points": member.monthly_points,
            })
        
        # Get chore counts with new meaningful categories
        today = datetime.utcnow().date()
        
        # Count all chores (non-archived)
        total_chores = await db.scalar(
            select(func.count()).select_from(Chore).where(Chore.is_archived == False)
        )
        
        # Count past due chores (overdue status)
        past_due_chores = await db.scalar(
            select(func.count()).select_from(Chore).where(
                and_(Chore.status == ChoreStatus.OVERDUE, Chore.is_archived == False)
            )
        )
        
        # Count open to work chores (pending status, due today or in past, not overdue)
        open_to_work_chores = await db.scalar(
            select(func.count()).select_from(Chore).where(
                and_(
                    Chore.status == ChoreStatus.PENDING,
                    Chore.is_archived == False,
                    or_(
                        Chore.due_date == None,  # No due date means always available
                        Chore.due_date <= today   # Due today or in the past
                    )
                )
            )
        )
        
        # Count upcoming chores (pending status, due in future)
        upcoming_chores = await db.scalar(
            select(func.count()).select_from(Chore).where(
                and_(
                    Chore.status == ChoreStatus.PENDING,
                    Chore.is_archived == False,
                    Chore.due_date > today
                )
            )
        )
        
        # Count completed chores (for recent activity)
        completed_chores = await db.scalar(
            select(func.count()).select_from(Chore).where(Chore.status == ChoreStatus.COMPLETED)
        )
        
        # Get today's completions
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = await db.scalar(
            select(func.count()).select_from(ChoreCompletion)
            .where(ChoreCompletion.completed_at >= today_start)
        )
        
        return {
            "members": members_data,
            "total_chores": total_chores,
            "past_due_chores": past_due_chores,
            "open_to_work_chores": open_to_work_chores,
            "upcoming_chores": upcoming_chores,
            "completed_chores": completed_chores,
            "completed_today": completed_today,
            # Combined actionable chores (past due + open to work)
            "actionable_chores": past_due_chores + open_to_work_chores,
            # Legacy fields for backward compatibility (can remove later)
            "pending_chores": open_to_work_chores + upcoming_chores,
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve dashboard data", operation="select")


@chores_router.post("/admin/reset-weekly", status_code=status.HTTP_200_OK)
async def admin_reset_weekly(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Manually trigger weekly points reset (admin only).
    """
    try:
        await reset_weekly_points(db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Weekly points reset successfully"}
        )
    except Exception as e:
        logger.error(f"Error in admin weekly reset: {e}", exc_info=True)
        raise DatabaseException("Failed to reset weekly points", operation="update")


@chores_router.post("/admin/reset-monthly", status_code=status.HTTP_200_OK)
async def admin_reset_monthly(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Manually trigger monthly points reset (admin only).
    """
    try:
        await reset_monthly_points(db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Monthly points reset successfully"}
        )
    except Exception as e:
        logger.error(f"Error in admin monthly reset: {e}", exc_info=True)
        raise DatabaseException("Failed to reset monthly points", operation="update")


@chores_router.post("/admin/update-overdue", status_code=status.HTTP_200_OK)
async def admin_update_overdue(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Manually trigger overdue status update for all chores.
    """
    try:
        from backend.services.chores import ChoreService
        updated_count = await ChoreService.update_overdue_status(db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Overdue status updated successfully",
                "updated_chores": updated_count
            }
        )
    except Exception as e:
        logger.error(f"Error updating overdue status: {e}", exc_info=True)
        raise DatabaseException("Failed to update overdue status", operation="update")


# ============================================================================
# CHORE ENDPOINTS (Parametric routes MUST come LAST)
# ============================================================================

@chores_router.get("", response_model=List[ChoreResponse])
async def list_chores(
    request: Request,
    status: Optional[ChoreStatus] = None,
    assigned_to_id: Optional[int] = None,
    category: Optional[ChoreCategory] = None,
    priority: Optional[ChorePriority] = None,
    db: AsyncSession = Depends(get_db)
) -> List[ChoreResponse]:
    """
    List all chores with optional filtering.
    """
    try:
        # Update overdue status before fetching chores
        from backend.services.chores import ChoreService
        await ChoreService.update_overdue_status(db)
        
        stmt = select(Chore).where(
            # Show non-archived chores OR completed chores from the last 7 days
            or_(
                Chore.is_archived == False,
                and_(
                    Chore.status == ChoreStatus.COMPLETED,
                    Chore.completed_at >= datetime.utcnow() - timedelta(days=7),
                    Chore.is_archived == True
                )
            )
        )
        
        # Apply filters
        if status:
            stmt = stmt.where(Chore.status == status)
        if assigned_to_id:
            stmt = stmt.where(Chore.assigned_to_id == assigned_to_id)
        if category:
            stmt = stmt.where(Chore.category == category)
        if priority:
            stmt = stmt.where(Chore.priority == priority)
        
        # Order by due date, then created date
        stmt = stmt.order_by(Chore.due_date.asc().nullslast(), Chore.created_at.desc())
        
        result = await db.execute(stmt)
        chores = result.scalars().all()
        
        # Build responses with member names
        responses = []
        for chore in chores:
            # Get creator name
            creator_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == chore.created_by_id)
            )
            creator = creator_result.scalar_one_or_none()
            
            # Get assignee name if assigned
            assignee_name = None
            if chore.assigned_to_id:
                assignee_result = await db.execute(
                    select(FamilyMember).where(FamilyMember.id == chore.assigned_to_id)
                )
                assignee = assignee_result.scalar_one_or_none()
                assignee_name = assignee.name if assignee else None
            
            responses.append(ChoreResponse(
                id=chore.id,
                title=chore.title,
                description=chore.description,
                points=chore.points,
                category=chore.category,
                priority=chore.priority,
                status=chore.status,
                recurrence_type=chore.recurrence_type,
                recurrence_interval=chore.recurrence_interval,
                assigned_to_id=chore.assigned_to_id,
                assigned_to_name=assignee_name,
                created_by_id=chore.created_by_id,
                created_by_name=creator.name if creator else "Unknown",
                estimated_minutes=chore.estimated_minutes,
                due_date=chore.due_date,
                next_due_date=chore.next_due_date,
                notes=chore.notes,
                created_at=chore.created_at,
                updated_at=chore.updated_at
            ))
        
        return responses
    except Exception as e:
        logger.error(f"Error listing chores: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve chores", operation="select")


@chores_router.get("/{chore_id}", response_model=ChoreResponse)
async def get_chore(
    request: Request,
    chore_id: int,
    db: AsyncSession = Depends(get_db)
) -> ChoreResponse:
    """
    Get a specific chore by ID.
    """
    try:
        result = await db.execute(select(Chore).where(Chore.id == chore_id))
        chore = result.scalar_one_or_none()
        
        if not chore:
            raise NotFoundException("Chore", str(chore_id))
        
        # Get creator name
        creator_result = await db.execute(
            select(FamilyMember).where(FamilyMember.id == chore.created_by_id)
        )
        creator = creator_result.scalar_one_or_none()
        
        # Get assignee name if assigned
        assignee_name = None
        if chore.assigned_to_id:
            assignee_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == chore.assigned_to_id)
            )
            assignee = assignee_result.scalar_one_or_none()
            assignee_name = assignee.name if assignee else None
        
        # Build response directly with all fields
        return ChoreResponse(
            id=chore.id,
            title=chore.title,
            description=chore.description,
            points=chore.points,
            category=chore.category,
            priority=chore.priority,
            status=chore.status,
            recurrence_type=chore.recurrence_type,
            recurrence_interval=chore.recurrence_interval,
            assigned_to_id=chore.assigned_to_id,
            assigned_to_name=assignee_name,
            created_by_id=chore.created_by_id,
            created_by_name=creator.name if creator else "Unknown",
            estimated_minutes=chore.estimated_minutes,
            due_date=chore.due_date,
            next_due_date=chore.next_due_date,
            notes=chore.notes,
            created_at=chore.created_at,
            updated_at=chore.updated_at
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting chore {chore_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve chore", operation="select")


@chores_router.post("/", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
async def create_chore(
    request: Request,
    chore: ChoreCreate,
    db: AsyncSession = Depends(get_db)
) -> ChoreResponse:
    """
    Create a new chore.
    """
    try:
        # Validate input
        if not chore.title or not chore.title.strip():
            raise ValidationException("Chore title is required")
        
        if len(chore.title.strip()) > 200:
            raise ValidationException("Chore title is too long (max 200 characters)")
        
        # Verify creator exists
        creator_result = await db.execute(
            select(FamilyMember).where(FamilyMember.id == chore.created_by_id)
        )
        creator = creator_result.scalar_one_or_none()
        if not creator:
            raise NotFoundException("Creator", str(chore.created_by_id))
        
        # Verify assigned member exists if provided
        assignee = None
        if chore.assigned_to_id:
            assignee_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == chore.assigned_to_id)
            )
            assignee = assignee_result.scalar_one_or_none()
            if not assignee:
                raise NotFoundException("Assigned member", str(chore.assigned_to_id))
        
        now = datetime.utcnow()
        
        # Default due_date to today if not provided
        due_date = chore.due_date
        if not due_date:
            due_date = now.date()
        
        db_chore = Chore(
            title=chore.title.strip(),
            description=chore.description,
            points=chore.points,
            category=chore.category,
            priority=chore.priority or ChorePriority.MEDIUM,
            status=ChoreStatus.PENDING,
            recurrence_type=getattr(chore, 'recurrence_type', None),  
            recurrence_interval=getattr(chore, 'recurrence_interval', None),
            assigned_to_id=chore.assigned_to_id,
            created_by_id=chore.created_by_id,
            estimated_minutes=chore.estimated_minutes,
            due_date=due_date,  # Use the defaulted due_date
            notes=chore.notes,
            created_at=now,
            updated_at=now
        )
        
        # Calculate next due date for recurring chores
        if db_chore.recurrence_type:
            db_chore.next_due_date = calculate_next_due_date(db_chore)
        
        db.add(db_chore)
        await db.commit()
        await db.refresh(db_chore)
        
        # Build response WITH member names - don't use model_validate directly
        return ChoreResponse(
            id=db_chore.id,
            title=db_chore.title,
            description=db_chore.description,
            points=db_chore.points,
            category=db_chore.category,
            priority=db_chore.priority,
            status=db_chore.status,
            recurrence_type=db_chore.recurrence_type,
            recurrence_interval=db_chore.recurrence_interval,
            assigned_to_id=db_chore.assigned_to_id,
            assigned_to_name=assignee.name if assignee else None,
            created_by_id=db_chore.created_by_id,
            created_by_name=creator.name,
            estimated_minutes=db_chore.estimated_minutes,
            due_date=db_chore.due_date,
            next_due_date=db_chore.next_due_date,
            notes=db_chore.notes,
            created_at=db_chore.created_at,
            updated_at=db_chore.updated_at
        )
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"Error creating chore: {e}", exc_info=True)
        raise DatabaseException("Failed to create chore", operation="insert")



@chores_router.put("/{chore_id}", response_model=ChoreResponse)
async def update_chore(
    request: Request,
    chore_id: int,
    chore_update: ChoreUpdate,
    db: AsyncSession = Depends(get_db)
) -> ChoreResponse:
    """
    Update an existing chore.
    """
    try:
        result = await db.execute(select(Chore).where(Chore.id == chore_id))
        chore = result.scalar_one_or_none()
        
        if not chore:
            raise NotFoundException("Chore", str(chore_id))
        
        # Verify assigned member exists if updating assignment
        update_data = chore_update.model_dump(exclude_unset=True)
        if "assigned_to_id" in update_data and update_data["assigned_to_id"]:
            assignee_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == update_data["assigned_to_id"])
            )
            assignee = assignee_result.scalar_one_or_none()
            if not assignee:
                raise NotFoundException("Assigned member", str(update_data["assigned_to_id"]))
        
        # Update fields
        for field, value in update_data.items():
            setattr(chore, field, value)
        
        # Recalculate next due date if recurrence changed
        if "recurrence_type" in update_data or "recurrence_interval" in update_data:
            chore.next_due_date = calculate_next_due_date(chore)
        
        chore.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(chore)
        
        # Get creator name
        creator_result = await db.execute(
            select(FamilyMember).where(FamilyMember.id == chore.created_by_id)
        )
        creator = creator_result.scalar_one_or_none()
        
        # Get assignee name if assigned
        assignee_name = None
        if chore.assigned_to_id:
            assignee_result = await db.execute(
                select(FamilyMember).where(FamilyMember.id == chore.assigned_to_id)
            )
            assignee = assignee_result.scalar_one_or_none()
            assignee_name = assignee.name if assignee else None
        
        # Build response directly with all fields
        return ChoreResponse(
            id=chore.id,
            title=chore.title,
            description=chore.description,
            points=chore.points,
            category=chore.category,
            priority=chore.priority,
            status=chore.status,
            recurrence_type=chore.recurrence_type,
            recurrence_interval=chore.recurrence_interval,
            assigned_to_id=chore.assigned_to_id,
            assigned_to_name=assignee_name,
            created_by_id=chore.created_by_id,
            created_by_name=creator.name if creator else "Unknown",
            estimated_minutes=chore.estimated_minutes,
            due_date=chore.due_date,
            next_due_date=chore.next_due_date,
            notes=chore.notes,
            created_at=chore.created_at,
            updated_at=chore.updated_at
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating chore {chore_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to update chore", operation="update")


@chores_router.delete("/{chore_id}")
async def delete_chore(
    request: Request,
    chore_id: int,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Delete a chore.
    """
    try:
        result = await db.execute(select(Chore).where(Chore.id == chore_id))
        chore = result.scalar_one_or_none()
        
        if not chore:
            raise NotFoundException("Chore", str(chore_id))
        
        await db.delete(chore)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Chore with ID {chore_id} deleted successfully"}
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chore {chore_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to delete chore", operation="delete")