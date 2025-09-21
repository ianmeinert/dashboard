"""
Family Chores Pydantic Schemas

Defines Pydantic models for request/response validation and serialization
for the family chore tracking system.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ChoreFrequencyEnum(str, Enum):
    """Chore frequency options."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ChoreStatusEnum(str, Enum):
    """Chore completion status."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    DISABLED = "DISABLED"


# Base schemas
class ParentBase(BaseModel):
    """Base parent schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Parent's name")
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN")

    @field_validator('pin')
    def validate_pin(cls, v):
        """Validate PIN is 4 digits."""
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v


class ParentCreate(ParentBase):
    """Schema for creating a parent."""
    pass


class ParentResponse(BaseModel):
    """Schema for parent response (with masked PIN)."""
    id: int
    name: str = Field(..., min_length=1, max_length=100, description="Parent's name")
    pin: str = Field(..., description="Masked PIN (always '****')")
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HouseholdMemberBase(BaseModel):
    """Base household member schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Member's name")
    date_of_birth: date = Field(..., description="Date of birth")
    is_parent: bool = Field(default=False, description="Whether member is a parent")


class HouseholdMemberCreate(HouseholdMemberBase):
    """Schema for creating a household member."""
    pass


class HouseholdMemberResponse(HouseholdMemberBase):
    """Schema for household member response."""
    id: int
    age: int = Field(..., description="Calculated age")
    age_category: str = Field(..., description="Age category for allowance calculation")
    is_active: bool
    parent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    """Base room schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Room name")
    description: Optional[str] = Field(None, max_length=500, description="Room description")
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")

    @field_validator('color_code')
    def validate_color_code(cls, v):
        """Validate hex color code format."""
        if v and not v.startswith('#'):
            v = '#' + v
        return v


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating a room."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None

    @field_validator('color_code')
    def validate_color_code(cls, v):
        """Validate hex color code format."""
        if v and not v.startswith('#'):
            v = '#' + v
        return v


class RoomResponse(RoomBase):
    """Schema for room response."""
    id: int
    is_active: bool
    parent_id: int
    created_at: datetime
    updated_at: datetime
    chore_count: Optional[int] = Field(None, description="Number of active chores in room")

    class Config:
        from_attributes = True


class ChoreBase(BaseModel):
    """Base chore schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Chore name")
    description: Optional[str] = Field(None, max_length=1000, description="Chore description")
    points: int = Field(..., ge=1, le=100, description="Points awarded for completion")
    frequency: ChoreFrequencyEnum = Field(..., description="How often the chore can be done")
    
    @field_validator('frequency', mode='before')
    @classmethod
    def normalize_frequency(cls, v):
        print(f"DEBUG: Validator called with value: '{v}', type: {type(v)}")
        if isinstance(v, str):
            result = v.upper()
            print(f"DEBUG: Converting '{v}' to '{result}'")
            return result
        print(f"DEBUG: Returning original value: {v}")
        return v


class ChoreCreate(ChoreBase):
    """Schema for creating a chore."""
    room_id: int = Field(..., description="ID of the room this chore belongs to")


class ChoreUpdate(BaseModel):
    """Schema for updating a chore."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    points: Optional[int] = Field(None, ge=1, le=100)
    frequency: Optional[ChoreFrequencyEnum] = None
    is_active: Optional[bool] = None


class ChoreResponse(ChoreBase):
    """Schema for chore response."""
    id: int
    is_active: bool
    room_id: int
    parent_id: int
    created_at: datetime
    updated_at: datetime
    last_completed_at: Optional[datetime]
    next_available_at: Optional[datetime]
    status: Optional[ChoreStatusEnum] = Field(None, description="Current status of the chore")
    completed_by: Optional[str] = Field(None, description="Name of member who completed it")
    room_name: Optional[str] = Field(None, description="Name of the room")

    class Config:
        from_attributes = True


class ChoreCompletionBase(BaseModel):
    """Base chore completion schema."""
    chore_id: int = Field(..., description="ID of the chore being completed")


class ChoreCompletionCreate(ChoreCompletionBase):
    """Schema for creating a chore completion."""
    pass


class ChoreCompletionConfirm(BaseModel):
    """Schema for confirming/rejecting a chore completion."""
    confirmed: bool = Field(..., description="True to confirm, False to reject")


class ChoreCompletionResponse(ChoreCompletionBase):
    """Schema for chore completion response."""
    id: int
    member_id: int
    parent_id: Optional[int]
    status: ChoreStatusEnum
    points_earned: int
    completed_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    week_start: date
    created_at: datetime
    member_name: Optional[str] = Field(None, description="Name of the member")
    chore_name: Optional[str] = Field(None, description="Name of the chore")

    # Point cap warning fields
    weekly_points_warning: Optional[dict] = Field(None, description="Warning info when approaching point cap")
    current_weekly_points: Optional[int] = Field(None, description="Current week points earned")
    weekly_points_remaining: Optional[int] = Field(None, description="Points remaining to reach cap")

    class Config:
        from_attributes = True


class WeeklyPointsResponse(BaseModel):
    """Schema for weekly points response."""
    id: int
    member_id: int
    week_start: date
    week_end: date
    points_earned: int
    points_capped: int
    member_name: Optional[str] = Field(None, description="Name of the member")

    class Config:
        from_attributes = True


class AllowanceCalculationResponse(BaseModel):
    """Schema for allowance calculation response."""
    id: int
    member_id: int
    month_year: str
    total_points_earned: int
    total_points_possible: int
    completion_percentage: float
    allowance_amount: float
    age_category: str
    calculated_at: datetime
    member_name: Optional[str] = Field(None, description="Name of the member")

    class Config:
        from_attributes = True


# Dashboard and summary schemas
class ChoreDashboardResponse(BaseModel):
    """Schema for chore dashboard data."""
    rooms: List[RoomResponse]
    chores: List[ChoreResponse]
    household_members: List[HouseholdMemberResponse]
    pending_completions: List[ChoreCompletionResponse]
    weekly_points: List[WeeklyPointsResponse]
    current_member: Optional[HouseholdMemberResponse] = None


class ParentDashboardResponse(BaseModel):
    """Schema for parent dashboard data."""
    rooms: List[RoomResponse]
    chores: List[ChoreResponse]
    household_members: List[HouseholdMemberResponse]
    pending_completions: List[ChoreCompletionResponse]
    weekly_points: List[WeeklyPointsResponse]
    allowance_calculations: List[AllowanceCalculationResponse]


class MemberSelectionResponse(BaseModel):
    """Schema for member selection response."""
    members: List[HouseholdMemberResponse]
    current_member: Optional[HouseholdMemberResponse] = None


class ChoreCompletionSummary(BaseModel):
    """Schema for chore completion summary."""
    total_chores: int
    completed_chores: int
    pending_chores: int
    disabled_chores: int
    completion_percentage: float


class WeeklyPointsSummary(BaseModel):
    """Schema for weekly points summary."""
    current_week_points: int
    max_weekly_points: int = 30
    points_remaining: int
    is_at_cap: bool


class AllowanceSummary(BaseModel):
    """Schema for allowance summary."""
    current_month_allowance: float
    total_points_earned: int
    total_points_possible: int
    completion_percentage: float
    age_category: str
    rate_per_point: float


# Error response schemas
class ChoreErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    message: str
    details: Optional[dict] = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    error: str = "validation_error"
    message: str
    field_errors: dict


# Success response schemas
class ChoreSuccessResponse(BaseModel):
    """Schema for success responses."""
    success: bool = True
    message: str
    data: Optional[dict] = None
