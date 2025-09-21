"""
Family Chores API Router

Provides REST API endpoints for managing family chores including
parent management, household members, rooms, chores, and allowance calculations.
"""

import logging
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.chore_errors import ChoreValidationException
from ..core.events import sse_manager
from ..core.exceptions import (DatabaseException, NotFoundException,
                               ValidationException)
from ..database_chores import get_chores_db
from ..models.schemas.chores import (AllowanceCalculationResponse,
                                     ChoreCompletionConfirm,
                                     ChoreCompletionCreate,
                                     ChoreCompletionResponse, ChoreCreate,
                                     ChoreDashboardResponse,
                                     ChoreErrorResponse, ChoreResponse,
                                     ChoreSuccessResponse, ChoreUpdate,
                                     HouseholdMemberCreate,
                                     HouseholdMemberResponse,
                                     MemberSelectionResponse, ParentCreate,
                                     ParentDashboardResponse, ParentResponse,
                                     RoomCreate, RoomResponse, RoomUpdate,
                                     WeeklyPointsResponse, WeeklyPointsSummary)
from ..services.chores_service import ChoresService
from ..services.monitoring_service import log_error, monitor_performance

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
chores_router = APIRouter()


# Parent Management Endpoints
@chores_router.get("/parents/exists")
@monitor_performance("/api/chores/parents/exists")
async def check_parents_exist(
    db: AsyncSession = Depends(get_chores_db)
) -> dict:
    """Check if any parents exist in the system."""
    try:
        service = ChoresService(db)
        count = await service.count_parents()
        
        return {
            "exists": count > 0,
            "count": count
        }
    except Exception as e:
        logger.error(f"Error checking if parents exist: {e}")
        raise HTTPException(status_code=500, detail="Failed to check parents")

@chores_router.post("/parents", response_model=ParentResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("/api/chores/parents")
@log_error("CHORES_PARENT_CREATE_ERROR")
async def create_parent(
    request: Request,
    parent_data: ParentCreate,
    db: AsyncSession = Depends(get_chores_db)
) -> ParentResponse:
    """Create a new parent with PIN authentication."""
    try:
        service = ChoresService(db)
        parent = await service.create_parent(parent_data)
        
        return ParentResponse(
            id=parent.id,
            name=parent.name,
            pin="****",  # Don't return actual PIN
            is_active=parent.is_active,
            created_at=parent.created_at,
            updated_at=parent.updated_at
        )
    except ValidationException as e:
        logger.warning(f"Validation error creating parent: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error creating parent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create parent")
    except Exception as e:
        logger.error(f"Unexpected error creating parent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create parent")


@chores_router.get("/parents/verify", response_model=ParentResponse)
@monitor_performance("/api/chores/parents/verify")
@log_error("CHORES_PARENT_VERIFY_ERROR")
async def verify_parent_pin(
    request: Request,
    name: str = Query(..., description="Parent name"),
    pin: str = Query(..., description="4-digit PIN"),
    db: AsyncSession = Depends(get_chores_db)
) -> ParentResponse:
    """Verify parent PIN and return parent info."""
    try:
        logger.info(f"Verifying parent: name={name}, pin_length={len(pin) if pin else 0}")
        
        service = ChoresService(db)
        parent = await service.verify_parent_pin(name, pin)
        
        if not parent:
            logger.warning(f"Parent verification failed for name: {name}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"Parent verification successful for: {parent.name}")
        return ParentResponse(
            id=parent.id,
            name=parent.name,
            pin="****",
            is_active=parent.is_active,
            created_at=parent.created_at,
            updated_at=parent.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying parent PIN: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify parent")


# Household Member Management Endpoints
@chores_router.post("/members", response_model=HouseholdMemberResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("/api/chores/members")
@log_error("CHORES_MEMBER_CREATE_ERROR")
async def create_household_member(
    request: Request,
    member_data: HouseholdMemberCreate,
    parent_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> HouseholdMemberResponse:
    """Create a new household member."""
    try:
        service = ChoresService(db)
        member = await service.create_household_member(member_data, parent_id)
        
        return HouseholdMemberResponse(
            id=member.id,
            name=member.name,
            date_of_birth=member.date_of_birth,
            is_parent=member.is_parent,
            age=member.age,
            age_category=member.age_category,
            is_active=member.is_active,
            parent_id=member.parent_id,
            created_at=member.created_at,
            updated_at=member.updated_at
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error creating household member: {e}")
        raise HTTPException(status_code=500, detail="Failed to create household member")


@chores_router.get("/members", response_model=List[HouseholdMemberResponse])
@monitor_performance("/api/chores/members")
@log_error("CHORES_MEMBERS_GET_ERROR")
async def get_household_members(
    request: Request,
    parent_id: int = Query(..., description="Parent ID"),
    db: AsyncSession = Depends(get_chores_db)
) -> List[HouseholdMemberResponse]:
    """Get all household members for a parent."""
    try:
        service = ChoresService(db)
        members = await service.get_household_members(parent_id)
        
        return [
            HouseholdMemberResponse(
                id=member.id,
                name=member.name,
                date_of_birth=member.date_of_birth,
                is_parent=member.is_parent,
                age=member.age,
                age_category=member.age_category,
                is_active=member.is_active,
                parent_id=member.parent_id,
                created_at=member.created_at,
                updated_at=member.updated_at
            )
            for member in members
        ]
    except DatabaseException as e:
        logger.error(f"Database error getting household members: {e}")
        raise HTTPException(status_code=500, detail="Failed to get household members")


@chores_router.get("/members/all", response_model=List[HouseholdMemberResponse])
@monitor_performance("/api/chores/members/all")
@log_error("CHORES_MEMBERS_ALL_GET_ERROR")
async def get_all_household_members(
    request: Request,
    db: AsyncSession = Depends(get_chores_db)
) -> List[HouseholdMemberResponse]:
    """Get all household members (for member selection without parent auth)."""
    try:
        service = ChoresService(db)
        members = await service.get_all_household_members()
        
        return [
            HouseholdMemberResponse(
                id=member.id,
                name=member.name,
                date_of_birth=member.date_of_birth,
                is_parent=member.is_parent,
                age=member.age,
                age_category=member.age_category,
                is_active=member.is_active,
                parent_id=member.parent_id,
                created_at=member.created_at,
                updated_at=member.updated_at
            )
            for member in members
        ]
    except DatabaseException as e:
        logger.error(f"Database error getting all household members: {e}")
        raise HTTPException(status_code=500, detail="Failed to get household members")


@chores_router.get("/members/{member_id}", response_model=HouseholdMemberResponse)
@monitor_performance("/api/chores/members/{member_id}")
@log_error("CHORES_MEMBER_GET_ERROR")
async def get_household_member(
    request: Request,
    member_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> HouseholdMemberResponse:
    """Get a specific household member."""
    try:
        service = ChoresService(db)
        member = await service.get_household_member(member_id)
        
        if not member:
            raise HTTPException(status_code=404, detail="Household member not found")
        
        return HouseholdMemberResponse(
            id=member.id,
            name=member.name,
            date_of_birth=member.date_of_birth,
            is_parent=member.is_parent,
            age=member.age,
            age_category=member.age_category,
            is_active=member.is_active,
            parent_id=member.parent_id,
            created_at=member.created_at,
            updated_at=member.updated_at
        )
    except HTTPException:
        raise
    except DatabaseException as e:
        logger.error(f"Database error getting household member: {e}")
        raise HTTPException(status_code=500, detail="Failed to get household member")


# Room Management Endpoints
@chores_router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("/api/chores/rooms")
@log_error("CHORES_ROOM_CREATE_ERROR")
async def create_room(
    request: Request,
    room_data: RoomCreate,
    parent_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> RoomResponse:
    """Create a new room."""
    try:
        service = ChoresService(db)
        room = await service.create_room(room_data, parent_id)
        
        return RoomResponse(
            id=room.id,
            name=room.name,
            description=room.description,
            color_code=room.color_code,
            is_active=room.is_active,
            parent_id=room.parent_id,
            created_at=room.created_at,
            updated_at=room.updated_at
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error creating room: {e}")
        raise HTTPException(status_code=500, detail="Failed to create room")


@chores_router.get("/rooms", response_model=List[RoomResponse])
@monitor_performance("/api/chores/rooms")
@log_error("CHORES_ROOMS_GET_ERROR")
async def get_rooms(
    request: Request,
    parent_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> List[RoomResponse]:
    """Get all rooms for a parent."""
    try:
        service = ChoresService(db)
        rooms = await service.get_rooms(parent_id)
        
        return [
            RoomResponse(
                id=room.id,
                name=room.name,
                description=room.description,
                color_code=room.color_code,
                is_active=room.is_active,
                parent_id=room.parent_id,
                created_at=room.created_at,
                updated_at=room.updated_at
            )
            for room in rooms
        ]
    except DatabaseException as e:
        logger.error(f"Database error getting rooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rooms")


@chores_router.put("/rooms/{room_id}", response_model=RoomResponse)
@monitor_performance("/api/chores/rooms/{room_id}")
@log_error("CHORES_ROOM_UPDATE_ERROR")
async def update_room(
    request: Request,
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_chores_db)
) -> RoomResponse:
    """Update a room."""
    try:
        service = ChoresService(db)
        room = await service.update_room(room_id, room_data)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return RoomResponse(
            id=room.id,
            name=room.name,
            description=room.description,
            color_code=room.color_code,
            is_active=room.is_active,
            parent_id=room.parent_id,
            created_at=room.created_at,
            updated_at=room.updated_at
        )
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error updating room: {e}")
        raise HTTPException(status_code=500, detail="Failed to update room")


@chores_router.delete("/rooms/{room_id}")
@monitor_performance("/api/chores/rooms/{room_id}")
@log_error("CHORES_ROOM_DELETE_ERROR")
async def delete_room(
    request: Request,
    room_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> JSONResponse:
    """Delete a room."""
    try:
        service = ChoresService(db)
        success = await service.delete_room(room_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Room deleted successfully"}
        )
    except HTTPException:
        raise
    except DatabaseException as e:
        logger.error(f"Database error deleting room: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete room")


# Chore Management Endpoints
@chores_router.post("/chores", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("/api/chores/chores")
@log_error("CHORES_CHORE_CREATE_ERROR")
async def create_chore(
    request: Request,
    chore_data: ChoreCreate,
    parent_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> ChoreResponse:
    """Create a new chore."""

    logger.info(f"Received chore_data: {chore_data}")
    logger.info(f"Frequency: {chore_data.frequency}")
    logger.info(f"Frequency type: {type(chore_data.frequency)}")
    
    try:
        service = ChoresService(db)
        chore = await service.create_chore(chore_data, parent_id)
        logger.info(f"Created chore: {chore}")
        return ChoreResponse(
            id=chore.id,
            name=chore.name,
            description=chore.description,
            points=chore.points,
            frequency=chore.frequency,
            is_active=chore.is_active,
            room_id=chore.room_id,
            parent_id=chore.parent_id,
            created_at=chore.created_at,
            updated_at=chore.updated_at,
            last_completed_at=chore.last_completed_at,
            next_available_at=chore.next_available_at
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error creating chore: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chore")


@chores_router.get("/chores", response_model=List[ChoreResponse])
@monitor_performance("/api/chores/chores")
@log_error("CHORES_CHORES_GET_ERROR")
async def get_chores(
    request: Request,
    parent_id: int,
    room_id: Optional[int] = None,
    db: AsyncSession = Depends(get_chores_db)
) -> List[ChoreResponse]:
    """Get all chores for a parent, optionally filtered by room."""
    try:
        service = ChoresService(db)
        chores = await service.get_chores(parent_id, room_id)
        
        return [
            ChoreResponse(
                id=chore.id,
                name=chore.name,
                description=chore.description,
                points=chore.points,
                frequency=chore.frequency,
                is_active=chore.is_active,
                room_id=chore.room_id,
                parent_id=chore.parent_id,
                created_at=chore.created_at,
                updated_at=chore.updated_at,
                last_completed_at=chore.last_completed_at,
                next_available_at=chore.next_available_at
            )
            for chore in chores
        ]
    except DatabaseException as e:
        logger.error(f"Database error getting chores: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chores")


@chores_router.put("/chores/{chore_id}", response_model=ChoreResponse)
@monitor_performance("/api/chores/chores/{chore_id}")
@log_error("CHORES_CHORE_UPDATE_ERROR")
async def update_chore(
    request: Request,
    chore_id: int,
    chore_data: ChoreUpdate,
    db: AsyncSession = Depends(get_chores_db)
) -> ChoreResponse:
    """Update a chore."""
    try:
        service = ChoresService(db)
        chore = await service.update_chore(chore_id, chore_data)
        
        if not chore:
            raise HTTPException(status_code=404, detail="Chore not found")
        
        return ChoreResponse(
            id=chore.id,
            name=chore.name,
            description=chore.description,
            points=chore.points,
            frequency=chore.frequency,
            is_active=chore.is_active,
            room_id=chore.room_id,
            parent_id=chore.parent_id,
            created_at=chore.created_at,
            updated_at=chore.updated_at,
            last_completed_at=chore.last_completed_at,
            next_available_at=chore.next_available_at
        )
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error updating chore: {e}")
        raise HTTPException(status_code=500, detail="Failed to update chore")


@chores_router.delete("/chores/{chore_id}")
@monitor_performance("/api/chores/chores/{chore_id}")
@log_error("CHORES_CHORE_DELETE_ERROR")
async def delete_chore(
    request: Request,
    chore_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> JSONResponse:
    """Delete a chore."""
    try:
        service = ChoresService(db)
        success = await service.delete_chore(chore_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chore not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Chore deleted successfully"}
        )
    except HTTPException:
        raise
    except DatabaseException as e:
        logger.error(f"Database error deleting chore: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chore")


# Chore Completion Endpoints
@chores_router.post("/chores/{chore_id}/complete", response_model=ChoreCompletionResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("/api/chores/chores/{chore_id}/complete")
@log_error("CHORES_CHORE_COMPLETE_ERROR")
async def complete_chore(
    request: Request,
    chore_id: int,
    member_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> ChoreCompletionResponse:
    """Mark a chore as completed by a household member."""
    try:
        service = ChoresService(db)
        completion = await service.complete_chore(chore_id, member_id)

        # Build response with optional warning information
        response_data = {
            "id": completion.id,
            "chore_id": completion.chore_id,
            "member_id": completion.member_id,
            "parent_id": completion.parent_id,
            "status": completion.status,
            "points_earned": completion.points_earned,
            "completed_at": completion.completed_at,
            "confirmed_at": completion.confirmed_at,
            "week_start": completion.week_start,
            "created_at": completion.created_at
        }

        # Add warning information if present
        if hasattr(completion, '_warning_info'):
            response_data["weekly_points_warning"] = completion._warning_info
            response_data["current_weekly_points"] = completion._current_weekly_points
            response_data["weekly_points_remaining"] = completion._weekly_points_remaining

        return ChoreCompletionResponse(**response_data)
    except ChoreValidationException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": "chore_validation_error",
                "message": e.message,
                "error_code": e.error_code,
                "user_message": e.user_message,
                "details": e.details
            }
        )
    except ValidationException as e:
        # Fallback for any remaining generic validation errors
        logger.info(f"COMPLETE_CHORE: Caught ValidationException: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error completing chore: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete chore")


@chores_router.post("/completions/{completion_id}/confirm", response_model=ChoreCompletionResponse)
@monitor_performance("/api/chores/completions/{completion_id}/confirm")
@log_error("CHORES_COMPLETION_CONFIRM_ERROR")
async def confirm_chore_completion(
    request: Request,
    completion_id: int,
    parent_id: int,
    confirmation_data: ChoreCompletionConfirm,
    db: AsyncSession = Depends(get_chores_db)
) -> ChoreCompletionResponse:
    """Confirm or reject a chore completion by parent."""
    try:
        service = ChoresService(db)
        completion = await service.confirm_chore_completion(
            completion_id,
            parent_id,
            confirmation_data.confirmed
        )
        
        return ChoreCompletionResponse(
            id=completion.id,
            chore_id=completion.chore_id,
            member_id=completion.member_id,
            parent_id=completion.parent_id,
            status=completion.status,
            points_earned=completion.points_earned,
            completed_at=completion.completed_at,
            confirmed_at=completion.confirmed_at,
            week_start=completion.week_start,
            created_at=completion.created_at
        )
    except ChoreValidationException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": "chore_validation_error",
                "message": e.message,
                "error_code": e.error_code,
                "user_message": e.user_message,
                "details": e.details
            }
        )
    except ValidationException as e:
        # Fallback for any remaining generic validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error confirming completion: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm completion")


@chores_router.get("/completions/pending", response_model=List[ChoreCompletionResponse])
@monitor_performance("/api/chores/completions/pending")
@log_error("CHORES_PENDING_COMPLETIONS_GET_ERROR")
async def get_pending_completions(
    request: Request,
    parent_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> List[ChoreCompletionResponse]:
    """Get all pending chore completions for a parent."""
    try:
        service = ChoresService(db)
        completions = await service.get_pending_completions(parent_id)
        
        return [
            ChoreCompletionResponse(
                id=completion.id,
                chore_id=completion.chore_id,
                member_id=completion.member_id,
                parent_id=completion.parent_id,
                status=completion.status,
                points_earned=completion.points_earned,
                completed_at=completion.completed_at,
                confirmed_at=completion.confirmed_at,
                week_start=completion.week_start,
                created_at=completion.created_at
            )
            for completion in completions
        ]
    except DatabaseException as e:
        logger.error(f"Database error getting pending completions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending completions")


# Dashboard Endpoints
@chores_router.get("/dashboard", response_model=ChoreDashboardResponse)
@monitor_performance("/api/chores/dashboard")
@log_error("CHORES_DASHBOARD_GET_ERROR")
async def get_chore_dashboard(
    request: Request,
    parent_id: int,
    member_id: Optional[int] = None,
    db: AsyncSession = Depends(get_chores_db)
) -> ChoreDashboardResponse:
    """Get chore dashboard data for a household member."""
    try:
        service = ChoresService(db)
        
        # Get all data
        rooms = await service.get_rooms(parent_id)
        chores = await service.get_chores(parent_id)
        members = await service.get_household_members(parent_id)
        pending_completions = await service.get_pending_completions(parent_id)
        
        # Get current member if specified
        current_member = None
        if member_id:
            current_member = await service.get_household_member(member_id)
        
        # Get weekly points for current member
        weekly_points = []
        if current_member:
            week_start = service._get_week_start(date.today())
            weekly_points_data = await service.get_weekly_points(current_member.id, week_start)
            if weekly_points_data:
                weekly_points = [weekly_points_data]
        
        return ChoreDashboardResponse(
            rooms=[RoomResponse(
                id=room.id,
                name=room.name,
                description=room.description,
                color_code=room.color_code,
                is_active=room.is_active,
                parent_id=room.parent_id,
                created_at=room.created_at,
                updated_at=room.updated_at
            ) for room in rooms],
            chores=[ChoreResponse(
                id=chore.id,
                name=chore.name,
                description=chore.description,
                points=chore.points,
                frequency=chore.frequency,
                is_active=chore.is_active,
                room_id=chore.room_id,
                parent_id=chore.parent_id,
                created_at=chore.created_at,
                updated_at=chore.updated_at,
                last_completed_at=chore.last_completed_at,
                next_available_at=chore.next_available_at
            ) for chore in chores],
            household_members=[HouseholdMemberResponse(
                id=member.id,
                name=member.name,
                date_of_birth=member.date_of_birth,
                is_parent=member.is_parent,
                age=member.age,
                age_category=member.age_category,
                is_active=member.is_active,
                parent_id=member.parent_id,
                created_at=member.created_at,
                updated_at=member.updated_at
            ) for member in members],
            pending_completions=[ChoreCompletionResponse(
                id=completion.id,
                chore_id=completion.chore_id,
                member_id=completion.member_id,
                parent_id=completion.parent_id,
                status=completion.status,
                points_earned=completion.points_earned,
                completed_at=completion.completed_at,
                confirmed_at=completion.confirmed_at,
                week_start=completion.week_start,
                created_at=completion.created_at
            ) for completion in pending_completions],
            weekly_points=[WeeklyPointsResponse(
                id=wp.id,
                member_id=wp.member_id,
                week_start=wp.week_start,
                week_end=wp.week_end,
                points_earned=wp.points_earned,
                points_capped=wp.points_capped
            ) for wp in weekly_points],
            current_member=HouseholdMemberResponse(
                id=current_member.id,
                name=current_member.name,
                date_of_birth=current_member.date_of_birth,
                is_parent=current_member.is_parent,
                age=current_member.age,
                age_category=current_member.age_category,
                is_active=current_member.is_active,
                parent_id=current_member.parent_id,
                created_at=current_member.created_at,
                updated_at=current_member.updated_at
            ) if current_member else None
        )
    except DatabaseException as e:
        logger.error(f"Database error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")


# Allowance Calculation Endpoints
@chores_router.get("/allowance/{member_id}/{month_year}", response_model=AllowanceCalculationResponse)
@monitor_performance("/api/chores/allowance/{member_id}/{month_year}")
@log_error("CHORES_ALLOWANCE_CALCULATE_ERROR")
async def calculate_allowance(
    request: Request,
    member_id: int,
    month_year: str,
    db: AsyncSession = Depends(get_chores_db)
) -> AllowanceCalculationResponse:
    """Calculate monthly allowance for a member."""
    try:
        service = ChoresService(db)
        calculation = await service.calculate_monthly_allowance(member_id, month_year)
        
        return AllowanceCalculationResponse(
            id=calculation.id,
            member_id=calculation.member_id,
            month_year=calculation.month_year,
            total_points_earned=calculation.total_points_earned,
            total_points_possible=calculation.total_points_possible,
            completion_percentage=calculation.completion_percentage,
            allowance_amount=calculation.allowance_amount,
            age_category=calculation.age_category,
            calculated_at=calculation.calculated_at
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error calculating allowance: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate allowance")


# Server-Sent Events Endpoints

@chores_router.get("/events/stream")
@monitor_performance("/api/chores/events/stream")
async def chore_events_stream(
    request: Request,
    parent_id: Optional[int] = Query(None, description="Parent ID to filter events")
):
    """
    Server-Sent Events stream for real-time chore updates.

    Events include:
    - chore_completed: When a chore is completed by a member
    - chore_confirmed: When a parent confirms/rejects a completion
    - points_updated: When weekly points change
    - chore_available: When a chore becomes available again
    """
    return await sse_manager.connect(request, parent_id)


@chores_router.get("/members/{member_id}/weekly-status", response_model=WeeklyPointsSummary)
@monitor_performance("/api/chores/members/{member_id}/weekly-status")
@log_error("CHORES_WEEKLY_STATUS_ERROR")
async def get_weekly_status(
    request: Request,
    member_id: int,
    db: AsyncSession = Depends(get_chores_db)
) -> WeeklyPointsSummary:
    """Get current weekly point status for a member with warnings."""
    try:
        service = ChoresService(db)

        # Get current week's points
        from datetime import date
        week_start = service._get_week_start(date.today())
        weekly_points = await service._get_weekly_points(member_id, week_start)

        current_points = weekly_points.points_capped if weekly_points else 0
        max_points = 30
        points_remaining = max(0, max_points - current_points)

        return WeeklyPointsSummary(
            current_week_points=current_points,
            max_weekly_points=max_points,
            points_remaining=points_remaining,
            is_at_cap=current_points >= max_points
        )
    except Exception as e:
        logger.error(f"Error getting weekly status for member {member_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weekly status")
