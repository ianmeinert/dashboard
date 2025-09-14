"""
Family Chores SQLAlchemy ORM Models

Defines the database models for the family chore tracking system including
parents, household members, rooms, chores, and chore completions.
"""

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (Boolean, Column, Date, DateTime, Enum, Float,
                        ForeignKey, Index, Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ChoreFrequencyEnum(PyEnum):
    """Chore frequency options."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ChoreStatusEnum(PyEnum):
    """Chore completion status."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DISABLED = "DISABLED"


class Parent(Base):
    """Parent user model for chore management."""
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    pin_hash = Column(String(255), nullable=False)  # Hashed 4-digit PIN
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Case-insensitive unique constraint on name
    __table_args__ = (
        Index('ix_parents_name_lower', func.lower(name), unique=True),
    )

    # Relationships
    household_members = relationship("HouseholdMember", back_populates="parent", cascade="all, delete-orphan")
    chore_completions = relationship("ChoreCompletion", back_populates="parent")

    def __repr__(self):
        return f"<Parent(id={self.id}, name='{self.name}')>"


class HouseholdMember(Base):
    """Household member model."""
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    is_parent = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="household_members")
    chore_completions = relationship("ChoreCompletion", back_populates="member")

    @property
    def age(self) -> int:
        """Calculate age from date of birth."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def age_category(self) -> str:
        """Get age category for allowance calculation."""
        age = self.age
        if age < 8:
            return "child"
        elif age <= 12:
            return "preteen"
        elif age <= 17:
            return "teenager"
        else:
            return "adult"

    def __repr__(self):
        return f"<HouseholdMember(id={self.id}, name='{self.name}', age={self.age})>"


class Room(Base):
    """Room model for organizing chores."""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, nullable=False, default=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    parent = relationship("Parent")
    chores = relationship("Chore", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}')>"


class Chore(Base):
    """Chore model for individual tasks."""
    __tablename__ = "chores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    points = Column(Integer, nullable=False, default=1)
    frequency = Column(Enum(ChoreFrequencyEnum), nullable=False, default=ChoreFrequencyEnum.DAILY)
    is_active = Column(Boolean, nullable=False, default=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_completed_at = Column(DateTime, nullable=True)
    next_available_at = Column(DateTime, nullable=True)

    # Relationships
    room = relationship("Room", back_populates="chores")
    parent = relationship("Parent")
    completions = relationship("ChoreCompletion", back_populates="chore", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chore(id={self.id}, name='{self.name}', points={self.points})>"


class ChoreCompletion(Base):
    """Chore completion tracking model."""
    __tablename__ = "chore_completions"

    id = Column(Integer, primary_key=True, index=True)
    chore_id = Column(Integer, ForeignKey("chores.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("household_members.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)  # For parent completions
    status = Column(Enum(ChoreStatusEnum), nullable=False, default=ChoreStatusEnum.PENDING)
    points_earned = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    week_start = Column(Date, nullable=False)  # For weekly point tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    chore = relationship("Chore", back_populates="completions")
    member = relationship("HouseholdMember", back_populates="chore_completions")
    parent = relationship("Parent", back_populates="chore_completions")

    # Indexes for performance
    __table_args__ = (
        Index('idx_chore_completion_week', 'member_id', 'week_start'),
        Index('idx_chore_completion_status', 'status'),
        Index('idx_chore_completion_chore', 'chore_id'),
    )

    def __repr__(self):
        return f"<ChoreCompletion(id={self.id}, chore_id={self.chore_id}, member_id={self.member_id}, status={self.status.value})>"


class WeeklyPoints(Base):
    """Weekly points tracking for allowance calculation."""
    __tablename__ = "weekly_points"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("household_members.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    points_earned = Column(Integer, nullable=False, default=0)
    points_capped = Column(Integer, nullable=False, default=0)  # Points after 30-point cap
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    member = relationship("HouseholdMember")

    # Indexes for performance
    __table_args__ = (
        Index('idx_weekly_points_member_week', 'member_id', 'week_start'),
    )

    def __repr__(self):
        return f"<WeeklyPoints(id={self.id}, member_id={self.member_id}, week_start={self.week_start}, points={self.points_earned})>"


class AllowanceCalculation(Base):
    """Monthly allowance calculations."""
    __tablename__ = "allowance_calculations"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("household_members.id"), nullable=False)
    month_year = Column(String(7), nullable=False)  # Format: "2024-01"
    total_points_earned = Column(Integer, nullable=False, default=0)
    total_points_possible = Column(Integer, nullable=False, default=0)
    completion_percentage = Column(Float, nullable=False, default=0.0)
    allowance_amount = Column(Float, nullable=False, default=0.0)
    age_category = Column(String(20), nullable=False)
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    member = relationship("HouseholdMember")

    # Indexes for performance
    __table_args__ = (
        Index('idx_allowance_member_month', 'member_id', 'month_year'),
    )

    def __repr__(self):
        return f"<AllowanceCalculation(id={self.id}, member_id={self.member_id}, month_year={self.month_year}, amount={self.allowance_amount})>"
