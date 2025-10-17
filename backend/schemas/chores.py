"""
Chores Module Pydantic Schemas
Request/Response schemas for the Chores API
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# Enums (matching database enums)
class ChoreStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ChorePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChoreCategory(str, Enum):
    CLEANING = "cleaning"
    COOKING = "cooking"
    DISHES = "dishes"
    LAUNDRY = "laundry"
    TRASH = "trash"
    PETS = "pets"
    YARD = "yard"
    MAINTENANCE = "maintenance"
    ORGANIZING = "organizing"
    OTHER = "other"


class RecurrencePattern(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


# ============================================================================
# Age Group Schemas
# ============================================================================

class AgeGroupBase(BaseModel):
    """Base age group schema"""
    name: str = Field(..., max_length=50, description="Age group name")
    min_age: int = Field(..., ge=0, le=100, description="Minimum age")
    max_age: int = Field(..., ge=0, le=100, description="Maximum age")
    default_weekly_cap: int = Field(..., ge=0, description="Default weekly points cap")


class AgeGroupCreate(AgeGroupBase):
    """Schema for creating an age group"""
    pass


class AgeGroupUpdate(BaseModel):
    """Schema for updating an age group"""
    name: Optional[str] = Field(None, max_length=50)
    min_age: Optional[int] = Field(None, ge=0, le=100)
    max_age: Optional[int] = Field(None, ge=0, le=100)
    default_weekly_cap: Optional[int] = Field(None, ge=0)


class AgeGroupResponse(AgeGroupBase):
    """Schema for age group response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Family Member Schemas
# ============================================================================

class FamilyMemberBase(BaseModel):
    """Base family member schema"""
    name: str = Field(..., max_length=100, description="Family member name")
    age: Optional[int] = Field(None, ge=0, le=100, description="Age")
    age_group_id: Optional[int] = Field(None, description="Age group ID")
    is_active: bool = Field(True, description="Is member active")


class FamilyMemberCreate(FamilyMemberBase):
    """Schema for creating a family member"""
    pass


class FamilyMemberUpdate(BaseModel):
    """Schema for updating a family member"""
    name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=100)
    age_group_id: Optional[int] = None
    weekly_points_cap: Optional[int] = Field(None, ge=0, description="Override weekly cap")
    is_active: Optional[bool] = None


class FamilyMemberResponse(FamilyMemberBase):
    """Schema for family member response"""
    id: int
    total_points: int
    monthly_points: int
    weekly_points: int
    weekly_points_cap: Optional[int]
    last_weekly_reset: Optional[date]
    last_monthly_reset: Optional[date]
    created_at: datetime
    updated_at: datetime
    age_group: Optional[AgeGroupResponse] = None

    model_config = ConfigDict(from_attributes=True)


class WeeklyStatus(BaseModel):
    """Weekly status for a family member"""
    member_id: int
    member_name: str
    weekly_points: int
    weekly_cap: int
    percentage: float = Field(..., ge=0, le=100, description="Percentage of cap used")
    can_complete_more: bool
    chores_completed_this_week: int


# ============================================================================
# Chore Schemas
# ============================================================================

class ChoreBase(BaseModel):
    """Base chore schema"""
    title: str = Field(..., max_length=200, description="Chore title")
    description: Optional[str] = Field(None, description="Chore description")
    points: int = Field(1, ge=1, le=10, description="Points for completion")
    category: ChoreCategory = Field(ChoreCategory.OTHER, description="Chore category")
    priority: ChorePriority = Field(ChorePriority.MEDIUM, description="Chore priority")
    due_date: Optional[date] = Field(None, description="Due date")
    is_recurring: bool = Field(False, description="Is this a recurring chore")
    recurrence_pattern: RecurrencePattern = Field(RecurrencePattern.NONE)
    recurrence_interval: int = Field(1, ge=1, description="Recurrence interval")
    notes: Optional[str] = Field(None, description="Additional notes")
    estimated_minutes: Optional[int] = Field(None, ge=0, description="Estimated time")


class ChoreCreate(ChoreBase):
    """Schema for creating a chore"""
    assigned_to_id: Optional[int] = Field(None, description="Assigned family member ID")
    created_by_id: int = Field(..., description="Creator family member ID")


class ChoreUpdate(BaseModel):
    """Schema for updating a chore"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    points: Optional[int] = Field(None, ge=1, le=10)
    category: Optional[ChoreCategory] = None
    priority: Optional[ChorePriority] = None
    assigned_to_id: Optional[int] = None
    due_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[ChoreStatus] = None


class ChoreResponse(ChoreBase):
    """Schema for chore response"""
    id: int
    assigned_to_id: Optional[int]
    created_by_id: int
    status: ChoreStatus
    next_occurrence: Optional[date]
    completed_at: Optional[datetime]
    completed_by_id: Optional[int]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships (optional)
    assigned_to: Optional["FamilyMemberResponse"] = None
    created_by: Optional["FamilyMemberResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class ChoreListResponse(BaseModel):
    """Schema for chore list with filters"""
    chores: List[ChoreResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ============================================================================
# Chore Completion Schemas
# ============================================================================

class ChoreCompletionCreate(BaseModel):
    """Schema for completing a chore"""
    chore_id: int = Field(..., description="Chore ID")
    completed_by_id: int = Field(..., description="Family member ID")
    notes: Optional[str] = Field(None, description="Completion notes")
    time_spent_minutes: Optional[int] = Field(None, ge=0, description="Time spent")
    verification_photo_url: Optional[str] = Field(None, max_length=500)


class ChoreCompletionResponse(BaseModel):
    """Schema for chore completion response"""
    id: int
    chore_id: int
    completed_by_id: int
    chore_title: str
    points_earned: int
    completed_at: datetime
    notes: Optional[str]
    time_spent_minutes: Optional[int]
    verification_photo_url: Optional[str]
    created_at: datetime
    
    completed_by: Optional[FamilyMemberResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Archive Schemas
# ============================================================================

class WeeklyPointsArchiveResponse(BaseModel):
    """Schema for weekly points archive"""
    id: int
    family_member_id: int
    week_start_date: date
    week_end_date: date
    points_earned: int
    weekly_cap: int
    chores_completed: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MonthlyPointsArchiveResponse(BaseModel):
    """Schema for monthly points archive"""
    id: int
    family_member_id: int
    year: int
    month: int
    points_earned: int
    chores_completed: int
    allowance_paid: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Statistics & Analytics Schemas
# ============================================================================

class ChoreStats(BaseModel):
    """Statistics for chores"""
    total_chores: int
    pending_chores: int
    completed_chores: int
    overdue_chores: int
    total_points_available: int


class MemberStats(BaseModel):
    """Statistics for a family member"""
    member_id: int
    member_name: str
    total_points: int
    monthly_points: int
    weekly_points: int
    chores_completed_today: int
    chores_completed_this_week: int
    chores_completed_this_month: int
    current_streak: int = Field(0, description="Consecutive days with completed chores")


class DashboardSummary(BaseModel):
    """Dashboard summary for chores module"""
    total_active_chores: int
    overdue_chores: int
    completed_today: int
    members_at_weekly_cap: int
    top_performers: List[MemberStats]
    chore_stats: ChoreStats


# ============================================================================
# Filter Schemas
# ============================================================================

class ChoreFilters(BaseModel):
    """Filters for chore queries"""
    status: Optional[ChoreStatus] = None
    category: Optional[ChoreCategory] = None
    priority: Optional[ChorePriority] = None
    assigned_to_id: Optional[int] = None
    is_recurring: Optional[bool] = None
    due_before: Optional[date] = None
    due_after: Optional[date] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)