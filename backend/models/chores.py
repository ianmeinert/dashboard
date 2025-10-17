from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from .base import Base

# Enums
class ChoreStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ChorePriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChoreCategory(str, PyEnum):
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


class RecurrencePattern(str, PyEnum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


# Models
class AgeGroup(Base):
    """Age group configuration for weekly point caps"""
    __tablename__ = "age_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "Young (5-10)", "Teen (11-15)"
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    default_weekly_cap = Column(Integer, nullable=False)  # Default points cap per week
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family_members = relationship("FamilyMember", back_populates="age_group")


class FamilyMember(Base):
    """Family member with points tracking"""
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    age_group_id = Column(Integer, ForeignKey("age_groups.id"), nullable=True)
    
    # Points tracking
    total_points = Column(Integer, default=0)  # All-time points
    monthly_points = Column(Integer, default=0)  # Current month (for allowance)
    weekly_points = Column(Integer, default=0)  # Current week (for cap tracking)
    weekly_points_cap = Column(Integer, nullable=True)  # Override default cap if set
    
    # Reset tracking
    last_weekly_reset = Column(Date, nullable=True)  # Last Monday reset date
    last_monthly_reset = Column(Date, nullable=True)  # Last month reset date
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    age_group = relationship("AgeGroup", back_populates="family_members")
    assigned_chores = relationship("Chore", back_populates="assigned_to", foreign_keys="Chore.assigned_to_id")
    created_chores = relationship("Chore", back_populates="created_by", foreign_keys="Chore.created_by_id")
    completions = relationship("ChoreCompletion", back_populates="completed_by")


class Chore(Base):
    """Chore/task model"""
    __tablename__ = "chores"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Points and categorization
    points = Column(Integer, default=1)  # Typically 1-3 points
    category = Column(Enum(ChoreCategory), default=ChoreCategory.OTHER)
    priority = Column(Enum(ChorePriority), default=ChorePriority.MEDIUM)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    
    # Status and timing
    status = Column(Enum(ChoreStatus), default=ChoreStatus.PENDING)
    due_date = Column(Date, nullable=True)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(Enum(RecurrencePattern), default=RecurrencePattern.NONE)
    recurrence_interval = Column(Integer, default=1)  # e.g., every 2 weeks
    next_occurrence = Column(Date, nullable=True)  # When this recurs next
    
    # Completion tracking
    completed_at = Column(DateTime, nullable=True)
    completed_by_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)  # Optional time estimate
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_to = relationship("FamilyMember", back_populates="assigned_chores", foreign_keys=[assigned_to_id])
    created_by = relationship("FamilyMember", back_populates="created_chores", foreign_keys=[created_by_id])
    completed_by = relationship("FamilyMember", foreign_keys=[completed_by_id])
    completion_history = relationship("ChoreCompletion", back_populates="chore", cascade="all, delete-orphan")


class ChoreCompletion(Base):
    """History of chore completions"""
    __tablename__ = "chore_completions"

    id = Column(Integer, primary_key=True, index=True)
    chore_id = Column(Integer, ForeignKey("chores.id"), nullable=False)
    completed_by_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    
    # Snapshot data (in case chore is modified later)
    chore_title = Column(String(200), nullable=False)
    points_earned = Column(Integer, nullable=False)
    
    # Completion details
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    verification_photo_url = Column(String(500), nullable=True)  # Future: photo verification
    
    # Time tracking (optional)
    time_spent_minutes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chore = relationship("Chore", back_populates="completion_history")
    completed_by = relationship("FamilyMember", back_populates="completions")


class WeeklyPointsArchive(Base):
    """Archive of weekly points before reset (for history/analytics)"""
    __tablename__ = "weekly_points_archive"

    id = Column(Integer, primary_key=True, index=True)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)  # Monday of that week
    week_end_date = Column(Date, nullable=False)  # Sunday of that week
    points_earned = Column(Integer, nullable=False)
    weekly_cap = Column(Integer, nullable=False)  # What their cap was that week
    chores_completed = Column(Integer, default=0)  # Number of chores
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    family_member = relationship("FamilyMember")


class MonthlyPointsArchive(Base):
    """Archive of monthly points (for allowance history)"""
    __tablename__ = "monthly_points_archive"

    id = Column(Integer, primary_key=True, index=True)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    points_earned = Column(Integer, nullable=False)
    chores_completed = Column(Integer, default=0)
    allowance_paid = Column(Float, nullable=True)  # Optional: track if allowance was paid
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    family_member = relationship("FamilyMember")