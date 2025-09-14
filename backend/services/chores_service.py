"""
Family Chores Service Layer

Provides business logic for the family chore tracking system including
authentication, room management, chore operations, and allowance calculations.
"""

import hashlib
import secrets
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..core.exceptions import (DatabaseException, NotFoundException,
                               ValidationException)
from ..models.chores import (AllowanceCalculation, Chore, ChoreCompletion,
                             ChoreFrequency, ChoreStatus, HouseholdMember,
                             Parent, Room, WeeklyPoints)
from ..models.schemas.chores import (ChoreCompletionCreate, ChoreCreate,
                                     ChoreUpdate, HouseholdMemberCreate,
                                     ParentCreate, RoomCreate, RoomUpdate)


class ChoresService:
    """Service class for family chores operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Parent Management
    async def create_parent(self, parent_data: ParentCreate) -> Parent:
        """Create a new parent with hashed PIN."""
        try:
            # Hash the PIN
            pin_hash = self._hash_pin(parent_data.pin)
            
            # Check if parent already exists (case-insensitive)
            existing_parent = await self.get_parent_by_name(parent_data.name)
            if existing_parent:
                raise ValidationException("Parent with this name already exists")

            parent = Parent(
                name=parent_data.name,
                pin_hash=pin_hash,
                is_active=True
            )
            
            self.db.add(parent)
            await self.db.commit()
            await self.db.refresh(parent)
            
            return parent
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e).lower()
            if ("unique constraint failed" in error_msg and "name" in error_msg) or \
               ("duplicate key" in error_msg) or \
               ("already exists" in error_msg):
                raise ValidationException("Parent with this name already exists")
            raise DatabaseException(f"Failed to create parent: {str(e)}", operation="insert")
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create parent: {str(e)}", operation="insert")

    async def verify_parent_pin(self, name: str, pin: str) -> Optional[Parent]:
        """Verify parent PIN and return parent if valid."""
        try:
            parent = await self.get_parent_by_name(name)
            
            if not parent:
                return None
                
            if self._verify_pin(pin, parent.pin_hash):
                return parent
            return None
        except Exception as e:
            raise DatabaseException(f"Failed to verify parent PIN: {str(e)}", operation="select")

    async def get_parent(self, parent_id: int) -> Optional[Parent]:
        """Get parent by ID."""
        try:
            result = await self.db.execute(
                select(Parent).where(Parent.id == parent_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get parent: {str(e)}", operation="select")

    async def get_parent_by_name(self, name: str) -> Optional[Parent]:
        """Get parent by name (case-insensitive)."""
        try:
            result = await self.db.execute(
                select(Parent).where(
                    and_(func.lower(Parent.name) == func.lower(name), Parent.is_active == True)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get parent by name: {str(e)}", operation="select")

    async def count_parents(self) -> int:
        """Count total number of active parents."""
        try:
            result = await self.db.execute(
                select(func.count(Parent.id)).where(Parent.is_active == True)
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseException(f"Failed to count parents: {str(e)}", operation="select")

    # Household Member Management
    async def create_household_member(self, member_data: HouseholdMemberCreate, parent_id: int) -> HouseholdMember:
        """Create a new household member."""
        try:
            member = HouseholdMember(
                name=member_data.name,
                date_of_birth=member_data.date_of_birth,
                is_parent=member_data.is_parent,
                parent_id=parent_id
            )
            
            self.db.add(member)
            await self.db.commit()
            await self.db.refresh(member)
            
            return member
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create household member: {str(e)}", operation="insert")

    async def get_household_members(self, parent_id: int) -> List[HouseholdMember]:
        """Get all household members for a parent."""
        try:
            result = await self.db.execute(
                select(HouseholdMember)
                .where(and_(HouseholdMember.parent_id == parent_id, HouseholdMember.is_active == True))
                .order_by(asc(HouseholdMember.name))
            )
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Failed to get household members: {str(e)}", operation="select")

    async def get_household_member(self, member_id: int) -> Optional[HouseholdMember]:
        """Get household member by ID."""
        try:
            result = await self.db.execute(
                select(HouseholdMember).where(HouseholdMember.id == member_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get household member: {str(e)}", operation="select")

    async def update_household_member(self, member_id: int, **updates) -> Optional[HouseholdMember]:
        """Update household member."""
        try:
            result = await self.db.execute(
                select(HouseholdMember).where(HouseholdMember.id == member_id)
            )
            member = result.scalar_one_or_none()
            
            if not member:
                return None
                
            for field, value in updates.items():
                if hasattr(member, field):
                    setattr(member, field, value)
            
            member.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(member)
            
            return member
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to update household member: {str(e)}", operation="update")

    # Room Management
    async def create_room(self, room_data: RoomCreate, parent_id: int) -> Room:
        """Create a new room."""
        try:
            room = Room(
                name=room_data.name,
                description=room_data.description,
                color_code=room_data.color_code,
                parent_id=parent_id
            )
            
            self.db.add(room)
            await self.db.commit()
            await self.db.refresh(room)
            
            return room
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create room: {str(e)}", operation="insert")

    async def get_rooms(self, parent_id: int) -> List[Room]:
        """Get all rooms for a parent."""
        try:
            result = await self.db.execute(
                select(Room)
                .where(and_(Room.parent_id == parent_id, Room.is_active == True))
                .order_by(asc(Room.name))
            )
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Failed to get rooms: {str(e)}", operation="select")

    async def get_room(self, room_id: int) -> Optional[Room]:
        """Get room by ID."""
        try:
            result = await self.db.execute(
                select(Room).where(Room.id == room_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get room: {str(e)}", operation="select")

    async def update_room(self, room_id: int, room_data: RoomUpdate) -> Optional[Room]:
        """Update room."""
        try:
            result = await self.db.execute(
                select(Room).where(Room.id == room_id)
            )
            room = result.scalar_one_or_none()
            
            if not room:
                return None
                
            update_data = room_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(room, field):
                    setattr(room, field, value)
            
            room.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(room)
            
            return room
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to update room: {str(e)}", operation="update")

    async def delete_room(self, room_id: int) -> bool:
        """Soft delete room by setting is_active to False."""
        try:
            result = await self.db.execute(
                select(Room).where(Room.id == room_id)
            )
            room = result.scalar_one_or_none()
            
            if not room:
                return False
                
            room.is_active = False
            room.updated_at = datetime.utcnow()
            await self.db.commit()
            
            return True
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to delete room: {str(e)}", operation="update")

    # Chore Management
    async def create_chore(self, chore_data: ChoreCreate, parent_id: int) -> Chore:
        """Create a new chore."""
        try:
            # Verify room exists and belongs to parent
            room = await self.get_room(chore_data.room_id)
            if not room or room.parent_id != parent_id:
                raise ValidationException("Room not found or access denied")

            chore = Chore(
                name=chore_data.name,
                description=chore_data.description,
                points=chore_data.points,
                frequency=chore_data.frequency,
                room_id=chore_data.room_id,
                parent_id=parent_id
            )
            
            self.db.add(chore)
            await self.db.commit()
            await self.db.refresh(chore)
            
            return chore
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create chore: {str(e)}", operation="insert")

    async def get_chores(self, parent_id: int, room_id: Optional[int] = None) -> List[Chore]:
        """Get all chores for a parent, optionally filtered by room."""
        try:
            query = select(Chore).where(
                and_(Chore.parent_id == parent_id, Chore.is_active == True)
            )
            
            if room_id:
                query = query.where(Chore.room_id == room_id)
                
            query = query.order_by(asc(Chore.name))
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Failed to get chores: {str(e)}", operation="select")

    async def get_chore(self, chore_id: int) -> Optional[Chore]:
        """Get chore by ID."""
        try:
            result = await self.db.execute(
                select(Chore).where(Chore.id == chore_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get chore: {str(e)}", operation="select")

    async def update_chore(self, chore_id: int, chore_data: ChoreUpdate) -> Optional[Chore]:
        """Update chore."""
        try:
            result = await self.db.execute(
                select(Chore).where(Chore.id == chore_id)
            )
            chore = result.scalar_one_or_none()
            
            if not chore:
                return None
                
            update_data = chore_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(chore, field):
                    setattr(chore, field, value)
            
            chore.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(chore)
            
            return chore
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to update chore: {str(e)}", operation="update")

    async def delete_chore(self, chore_id: int) -> bool:
        """Soft delete chore by setting is_active to False."""
        try:
            result = await self.db.execute(
                select(Chore).where(Chore.id == chore_id)
            )
            chore = result.scalar_one_or_none()
            
            if not chore:
                return False
                
            chore.is_active = False
            chore.updated_at = datetime.utcnow()
            await self.db.commit()
            
            return True
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to delete chore: {str(e)}", operation="update")

    # Chore Completion Management
    async def complete_chore(self, chore_id: int, member_id: int) -> ChoreCompletion:
        """Mark a chore as completed by a household member."""
        try:
            # Get chore and member
            chore = await self.get_chore(chore_id)
            member = await self.get_household_member(member_id)
            
            if not chore or not member:
                raise ValidationException("Chore or member not found")
            
            if not chore.is_active:
                raise ValidationException("Chore is not active")
            
            # Check if chore is available (not disabled due to frequency)
            if chore.next_available_at and chore.next_available_at > datetime.utcnow():
                raise ValidationException("Chore is not available yet due to frequency restrictions")
            
            # Check weekly point cap
            week_start = self._get_week_start(date.today())
            weekly_points = await self._get_weekly_points(member_id, week_start)
            
            if weekly_points and weekly_points.points_capped >= 30:
                raise ValidationException("Weekly point cap reached (30 points)")
            
            # Create completion record
            completion = ChoreCompletion(
                chore_id=chore_id,
                member_id=member_id,
                status=ChoreStatus.PENDING,
                points_earned=chore.points,
                week_start=week_start
            )
            
            self.db.add(completion)
            
            # Update chore last completed time
            chore.last_completed_at = datetime.utcnow()
            chore.next_available_at = self._calculate_next_available(chore.frequency)
            
            await self.db.commit()
            await self.db.refresh(completion)
            
            # Update weekly points
            await self._update_weekly_points(member_id, week_start, chore.points)
            
            return completion
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to complete chore: {str(e)}", operation="insert")

    async def confirm_chore_completion(self, completion_id: int, parent_id: int) -> ChoreCompletion:
        """Confirm a chore completion by parent."""
        try:
            result = await self.db.execute(
                select(ChoreCompletion)
                .where(and_(
                    ChoreCompletion.id == completion_id,
                    ChoreCompletion.status == ChoreStatus.PENDING
                ))
            )
            completion = result.scalar_one_or_none()
            
            if not completion:
                raise ValidationException("Pending completion not found")
            
            # Verify parent has access to this completion
            chore = await self.get_chore(completion.chore_id)
            if not chore or chore.parent_id != parent_id:
                raise ValidationException("Access denied")
            
            # Update completion status
            completion.status = ChoreStatus.COMPLETED
            completion.confirmed_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(completion)
            
            return completion
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to confirm chore completion: {str(e)}", operation="update")

    async def get_pending_completions(self, parent_id: int) -> List[ChoreCompletion]:
        """Get all pending chore completions for a parent."""
        try:
            result = await self.db.execute(
                select(ChoreCompletion)
                .join(Chore, ChoreCompletion.chore_id == Chore.id)
                .where(and_(
                    Chore.parent_id == parent_id,
                    ChoreCompletion.status == ChoreStatus.PENDING
                ))
                .order_by(desc(ChoreCompletion.created_at))
            )
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Failed to get pending completions: {str(e)}", operation="select")

    # Weekly Points and Allowance Management
    async def get_weekly_points(self, member_id: int, week_start: Optional[date] = None) -> Optional[WeeklyPoints]:
        """Get weekly points for a member."""
        if not week_start:
            week_start = self._get_week_start(date.today())
            
        try:
            result = await self.db.execute(
                select(WeeklyPoints).where(
                    and_(
                        WeeklyPoints.member_id == member_id,
                        WeeklyPoints.week_start == week_start
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get weekly points: {str(e)}", operation="select")

    async def calculate_monthly_allowance(self, member_id: int, month_year: str) -> AllowanceCalculation:
        """Calculate monthly allowance for a member."""
        try:
            member = await self.get_household_member(member_id)
            if not member:
                raise ValidationException("Member not found")
            
            # Get 4 weeks of data for the month
            month_start = datetime.strptime(f"{month_year}-01", "%Y-%m-%d").date()
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Get weekly points for the month
            result = await self.db.execute(
                select(WeeklyPoints).where(
                    and_(
                        WeeklyPoints.member_id == member_id,
                        WeeklyPoints.week_start >= month_start,
                        WeeklyPoints.week_start <= month_end
                    )
                )
            )
            weekly_points = result.scalars().all()
            
            total_points_earned = sum(wp.points_capped for wp in weekly_points)
            total_points_possible = min(len(weekly_points) * 30, 120)  # Max 30 points per week, 4 weeks max
            completion_percentage = (total_points_earned / total_points_possible) if total_points_possible > 0 else 0
            
            # Calculate allowance based on age category
            age_category = member.age_category
            if age_category == "adult":
                allowance_amount = 0.0
            elif age_category == "teenager":
                rate_per_point = member.age  # $1 per year of age
                allowance_amount = completion_percentage * rate_per_point
            else:  # preteen
                rate_per_point = 0.50
                allowance_amount = completion_percentage * total_points_possible * rate_per_point
            
            # Create or update allowance calculation
            result = await self.db.execute(
                select(AllowanceCalculation).where(
                    and_(
                        AllowanceCalculation.member_id == member_id,
                        AllowanceCalculation.month_year == month_year
                    )
                )
            )
            calculation = result.scalar_one_or_none()
            
            if calculation:
                calculation.total_points_earned = total_points_earned
                calculation.total_points_possible = total_points_possible
                calculation.completion_percentage = completion_percentage
                calculation.allowance_amount = allowance_amount
                calculation.age_category = age_category
                calculation.calculated_at = datetime.utcnow()
            else:
                calculation = AllowanceCalculation(
                    member_id=member_id,
                    month_year=month_year,
                    total_points_earned=total_points_earned,
                    total_points_possible=total_points_possible,
                    completion_percentage=completion_percentage,
                    allowance_amount=allowance_amount,
                    age_category=age_category
                )
                self.db.add(calculation)
            
            await self.db.commit()
            await self.db.refresh(calculation)
            
            return calculation
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to calculate allowance: {str(e)}", operation="insert")

    # Helper methods
    def _hash_pin(self, pin: str) -> str:
        """Hash a 4-digit PIN."""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex() + ':' + salt

    def _verify_pin(self, pin: str, pin_hash: str) -> bool:
        """Verify a 4-digit PIN against its hash."""
        try:
            hash_part, salt = pin_hash.split(':')
            return hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex() == hash_part
        except:
            return False

    def _get_week_start(self, date_obj: date) -> date:
        """Get the start of the week (Monday) for a given date."""
        return date_obj - timedelta(days=date_obj.weekday())

    def _calculate_next_available(self, frequency: ChoreFrequency) -> datetime:
        """Calculate when a chore will be available again based on frequency."""
        now = datetime.utcnow()
        
        if frequency == ChoreFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ChoreFrequency.WEEKLY:
            # Next Monday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            return now + timedelta(days=days_until_monday)
        elif frequency == ChoreFrequency.MONTHLY:
            # First day of next month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            return next_month
        else:
            return now

    async def _get_weekly_points(self, member_id: int, week_start: date) -> Optional[WeeklyPoints]:
        """Get or create weekly points record."""
        result = await self.db.execute(
            select(WeeklyPoints).where(
                and_(
                    WeeklyPoints.member_id == member_id,
                    WeeklyPoints.week_start == week_start
                )
            )
        )
        return result.scalar_one_or_none()

    async def _update_weekly_points(self, member_id: int, week_start: date, points: int):
        """Update weekly points with cap enforcement."""
        weekly_points = await self._get_weekly_points(member_id, week_start)
        
        if not weekly_points:
            # Create new weekly points record
            weekly_points = WeeklyPoints(
                member_id=member_id,
                week_start=week_start,
                week_end=week_start + timedelta(days=6),
                points_earned=points,
                points_capped=min(points, 30)
            )
            self.db.add(weekly_points)
        else:
            # Update existing record
            new_points = weekly_points.points_earned + points
            weekly_points.points_earned = new_points
            weekly_points.points_capped = min(new_points, 30)
        
        await self.db.commit()
