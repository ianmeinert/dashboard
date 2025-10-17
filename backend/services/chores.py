"""
Chores Module - Service Layer
Business logic for chores, family members, and points management
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.chores import (
    AgeGroup, FamilyMember, Chore, ChoreCompletion,
    WeeklyPointsArchive, MonthlyPointsArchive,
    ChoreStatus, RecurrencePattern
)
from ..schemas.chores import (
    AgeGroupCreate, AgeGroupUpdate,
    FamilyMemberCreate, FamilyMemberUpdate,
    ChoreCreate, ChoreUpdate, ChoreCompletionCreate,
    ChoreFilters, WeeklyStatus
)


# ============================================================================
# Helper Functions
# ============================================================================

def get_week_start_date(target_date: date = None) -> date:
    """Get the Monday of the week for a given date."""
    if target_date is None:
        target_date = date.today()
    return target_date - timedelta(days=target_date.weekday())


def get_week_end_date(target_date: date = None) -> date:
    """Get the Sunday of the week for a given date."""
    week_start = get_week_start_date(target_date)
    return week_start + timedelta(days=6)


def get_month_start_date(target_date: date = None) -> date:
    """Get the first day of the month."""
    if target_date is None:
        target_date = date.today()
    return target_date.replace(day=1)


def calculate_next_occurrence(
    current_date: date,
    pattern: RecurrencePattern,
    interval: int = 1
) -> date:
    """Calculate the next occurrence date based on recurrence pattern."""
    if pattern == RecurrencePattern.DAILY:
        return current_date + timedelta(days=interval)
    elif pattern == RecurrencePattern.WEEKLY:
        return current_date + timedelta(weeks=interval)
    elif pattern == RecurrencePattern.BIWEEKLY:
        return current_date + timedelta(weeks=2 * interval)
    elif pattern == RecurrencePattern.MONTHLY:
        # Handle month boundaries
        month = current_date.month + interval
        year = current_date.year
        while month > 12:
            month -= 12
            year += 1
        return current_date.replace(year=year, month=month)
    return current_date


# ============================================================================
# Age Group Service
# ============================================================================

class AgeGroupService:
    """Service for managing age groups"""
    
    @staticmethod
    async def create(session: AsyncSession, data: AgeGroupCreate) -> AgeGroup:
        """Create a new age group."""
        age_group = AgeGroup(**data.model_dump())
        session.add(age_group)
        await session.commit()
        await session.refresh(age_group)
        return age_group
    
    @staticmethod
    async def get_by_id(session: AsyncSession, age_group_id: int) -> Optional[AgeGroup]:
        """Get age group by ID."""
        result = await session.execute(
            select(AgeGroup).where(AgeGroup.id == age_group_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List[AgeGroup]:
        """Get all age groups."""
        result = await session.execute(select(AgeGroup).order_by(AgeGroup.min_age))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        session: AsyncSession,
        age_group_id: int,
        data: AgeGroupUpdate
    ) -> Optional[AgeGroup]:
        """Update an age group."""
        age_group = await AgeGroupService.get_by_id(session, age_group_id)
        if not age_group:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(age_group, field, value)
        
        await session.commit()
        await session.refresh(age_group)
        return age_group
    
    @staticmethod
    async def delete(session: AsyncSession, age_group_id: int) -> bool:
        """Delete an age group."""
        result = await session.execute(
            delete(AgeGroup).where(AgeGroup.id == age_group_id)
        )
        await session.commit()
        return result.rowcount > 0


# ============================================================================
# Family Member Service
# ============================================================================

class FamilyMemberService:
    """Service for managing family members"""
    
    @staticmethod
    async def create(session: AsyncSession, data: FamilyMemberCreate) -> FamilyMember:
        """Create a new family member."""
        member = FamilyMember(**data.model_dump())
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member
    
    @staticmethod
    async def get_by_id(session: AsyncSession, member_id: int) -> Optional[FamilyMember]:
        """Get family member by ID with age group relationship."""
        result = await session.execute(
            select(FamilyMember)
            .options(selectinload(FamilyMember.age_group))
            .where(FamilyMember.id == member_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(session: AsyncSession, active_only: bool = True) -> List[FamilyMember]:
        """Get all family members."""
        query = select(FamilyMember).options(selectinload(FamilyMember.age_group))
        if active_only:
            query = query.where(FamilyMember.is_active == True)
        
        result = await session.execute(query.order_by(FamilyMember.name))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        session: AsyncSession,
        member_id: int,
        data: FamilyMemberUpdate
    ) -> Optional[FamilyMember]:
        """Update a family member."""
        member = await FamilyMemberService.get_by_id(session, member_id)
        if not member:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)
        
        await session.commit()
        await session.refresh(member)
        return member
    
    @staticmethod
    async def get_weekly_cap(member: FamilyMember) -> int:
        """Get the effective weekly cap for a member."""
        if member.weekly_points_cap is not None:
            return member.weekly_points_cap
        if member.age_group:
            return member.age_group.default_weekly_cap
        return 30  # Default fallback
    
    @staticmethod
    async def get_weekly_status(
        session: AsyncSession,
        member_id: int
    ) -> Optional[WeeklyStatus]:
        """Get weekly status for a member."""
        member = await FamilyMemberService.get_by_id(session, member_id)
        if not member:
            return None
        
        weekly_cap = await FamilyMemberService.get_weekly_cap(member)
        percentage = (member.weekly_points / weekly_cap * 100) if weekly_cap > 0 else 0
        can_complete_more = member.weekly_points < weekly_cap
        
        # Count chores completed this week
        week_start = get_week_start_date()
        result = await session.execute(
            select(func.count(ChoreCompletion.id))
            .where(
                and_(
                    ChoreCompletion.completed_by_id == member_id,
                    ChoreCompletion.completed_at >= week_start
                )
            )
        )
        chores_count = result.scalar() or 0
        
        return WeeklyStatus(
            member_id=member.id,
            member_name=member.name,
            weekly_points=member.weekly_points,
            weekly_cap=weekly_cap,
            percentage=round(percentage, 2),
            can_complete_more=can_complete_more,
            chores_completed_this_week=chores_count
        )
    
    @staticmethod
    async def check_and_reset_weekly_points(
        session: AsyncSession,
        member: FamilyMember
    ) -> bool:
        """Check if weekly reset is needed and perform it."""
        today = date.today()
        current_week_start = get_week_start_date(today)
        
        # Check if we need to reset
        if member.last_weekly_reset is None or member.last_weekly_reset < current_week_start:
            # Archive current week's points
            if member.weekly_points > 0:
                await FamilyMemberService.archive_weekly_points(session, member)
            
            # Reset weekly points
            member.weekly_points = 0
            member.last_weekly_reset = current_week_start
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def archive_weekly_points(session: AsyncSession, member: FamilyMember) -> None:
        """Archive weekly points before reset."""
        if member.last_weekly_reset:
            week_start = member.last_weekly_reset
        else:
            week_start = get_week_start_date(date.today() - timedelta(days=7))
        
        week_end = get_week_end_date(week_start)
        weekly_cap = await FamilyMemberService.get_weekly_cap(member)
        
        # Count chores completed in that week
        result = await session.execute(
            select(func.count(ChoreCompletion.id))
            .where(
                and_(
                    ChoreCompletion.completed_by_id == member.id,
                    ChoreCompletion.completed_at >= week_start,
                    ChoreCompletion.completed_at <= week_end
                )
            )
        )
        chores_count = result.scalar() or 0
        
        archive = WeeklyPointsArchive(
            family_member_id=member.id,
            week_start_date=week_start,
            week_end_date=week_end,
            points_earned=member.weekly_points,
            weekly_cap=weekly_cap,
            chores_completed=chores_count
        )
        session.add(archive)
    
    @staticmethod
    async def check_and_reset_monthly_points(
        session: AsyncSession,
        member: FamilyMember
    ) -> bool:
        """Check if monthly reset is needed and perform it."""
        today = date.today()
        current_month_start = get_month_start_date(today)
        
        # Check if we need to reset
        if member.last_monthly_reset is None or member.last_monthly_reset < current_month_start:
            # Archive current month's points
            if member.monthly_points > 0:
                await FamilyMemberService.archive_monthly_points(session, member)
            
            # Reset monthly points
            member.monthly_points = 0
            member.last_monthly_reset = current_month_start
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def archive_monthly_points(session: AsyncSession, member: FamilyMember) -> None:
        """Archive monthly points before reset."""
        if member.last_monthly_reset:
            month_start = member.last_monthly_reset
        else:
            # Default to last month
            today = date.today()
            if today.month == 1:
                month_start = date(today.year - 1, 12, 1)
            else:
                month_start = date(today.year, today.month - 1, 1)
        
        # Count chores completed in that month
        # Calculate month end
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
        
        result = await session.execute(
            select(func.count(ChoreCompletion.id))
            .where(
                and_(
                    ChoreCompletion.completed_by_id == member.id,
                    ChoreCompletion.completed_at >= month_start,
                    ChoreCompletion.completed_at <= month_end
                )
            )
        )
        chores_count = result.scalar() or 0
        
        archive = MonthlyPointsArchive(
            family_member_id=member.id,
            year=month_start.year,
            month=month_start.month,
            points_earned=member.monthly_points,
            chores_completed=chores_count
        )
        session.add(archive)


# ============================================================================
# Chore Service
# ============================================================================

class ChoreService:
    """Service for managing chores"""
    
    @staticmethod
    async def create(session: AsyncSession, data: ChoreCreate) -> Chore:
        """Create a new chore."""
        chore_data = data.model_dump()
        
        # Handle recurrence
        if chore_data.get('is_recurring') and chore_data.get('recurrence_pattern') != RecurrencePattern.NONE:
            if not chore_data.get('next_occurrence'):
                chore_data['next_occurrence'] = calculate_next_occurrence(
                    date.today(),
                    chore_data['recurrence_pattern'],
                    chore_data.get('recurrence_interval', 1)
                )
        
        chore = Chore(**chore_data)
        session.add(chore)
        await session.commit()
        await session.refresh(chore)
        return chore
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        chore_id: int,
        include_relationships: bool = False
    ) -> Optional[Chore]:
        """Get chore by ID."""
        query = select(Chore).where(Chore.id == chore_id)
        
        if include_relationships:
            query = query.options(
                selectinload(Chore.assigned_to),
                selectinload(Chore.created_by)
            )
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
        filters: Optional[ChoreFilters] = None,
        include_archived: bool = False
    ) -> Tuple[List[Chore], int]:
        """Get all chores with optional filters and pagination."""
        query = select(Chore).options(
            selectinload(Chore.assigned_to),
            selectinload(Chore.created_by)
        )
        
        # Apply archived filter
        if not include_archived:
            query = query.where(Chore.is_archived == False)
        
        # Apply filters if provided
        if filters:
            if filters.status:
                query = query.where(Chore.status == filters.status)
            if filters.category:
                query = query.where(Chore.category == filters.category)
            if filters.priority:
                query = query.where(Chore.priority == filters.priority)
            if filters.assigned_to_id:
                query = query.where(Chore.assigned_to_id == filters.assigned_to_id)
            if filters.is_recurring is not None:
                query = query.where(Chore.is_recurring == filters.is_recurring)
            if filters.due_before:
                query = query.where(Chore.due_date <= filters.due_before)
            if filters.due_after:
                query = query.where(Chore.due_date >= filters.due_after)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        if filters:
            offset = (filters.page - 1) * filters.page_size
            query = query.offset(offset).limit(filters.page_size)
        
        # Order by priority and due date
        query = query.order_by(
            Chore.priority.desc(),
            Chore.due_date.asc(),
            Chore.created_at.desc()
        )
        
        result = await session.execute(query)
        chores = list(result.scalars().all())
        
        return chores, total
    
    @staticmethod
    async def update(
        session: AsyncSession,
        chore_id: int,
        data: ChoreUpdate
    ) -> Optional[Chore]:
        """Update a chore."""
        chore = await ChoreService.get_by_id(session, chore_id)
        if not chore:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chore, field, value)
        
        await session.commit()
        await session.refresh(chore)
        return chore
    
    @staticmethod
    async def delete(session: AsyncSession, chore_id: int) -> bool:
        """Delete a chore (soft delete by archiving)."""
        chore = await ChoreService.get_by_id(session, chore_id)
        if not chore:
            return False
        
        chore.is_archived = True
        await session.commit()
        return True
    
    @staticmethod
    async def complete_chore(
        session: AsyncSession,
        data: ChoreCompletionCreate
    ) -> Tuple[Optional[ChoreCompletion], Optional[str]]:
        """
        Complete a chore and award points.
        Returns (completion, error_message)
        """
        # Get chore and member
        chore = await ChoreService.get_by_id(session, data.chore_id)
        if not chore:
            return None, "Chore not found"
        
        member = await FamilyMemberService.get_by_id(session, data.completed_by_id)
        if not member:
            return None, "Family member not found"
        
        # Check if member has exceeded weekly cap
        await FamilyMemberService.check_and_reset_weekly_points(session, member)
        weekly_cap = await FamilyMemberService.get_weekly_cap(member)
        
        if member.weekly_points + chore.points > weekly_cap:
            return None, f"Weekly cap reached ({weekly_cap} points/week). Come back Monday!"
        
        # Create completion record
        completion = ChoreCompletion(
            chore_id=chore.id,
            completed_by_id=member.id,
            chore_title=chore.title,
            points_earned=chore.points,
            notes=data.notes,
            time_spent_minutes=data.time_spent_minutes,
            verification_photo_url=data.verification_photo_url
        )
        session.add(completion)
        
        # Award points
        member.total_points += chore.points
        member.monthly_points += chore.points
        member.weekly_points += chore.points
        
        # Update chore status
        chore.status = ChoreStatus.COMPLETED
        chore.completed_at = datetime.utcnow()
        chore.completed_by_id = member.id
        
        # Handle recurring chores
        if chore.is_recurring and chore.recurrence_pattern != RecurrencePattern.NONE:
            # Create next occurrence
            next_chore = Chore(
                title=chore.title,
                description=chore.description,
                points=chore.points,
                category=chore.category,
                priority=chore.priority,
                assigned_to_id=chore.assigned_to_id,
                created_by_id=chore.created_by_id,
                is_recurring=True,
                recurrence_pattern=chore.recurrence_pattern,
                recurrence_interval=chore.recurrence_interval,
                notes=chore.notes,
                estimated_minutes=chore.estimated_minutes,
                due_date=calculate_next_occurrence(
                    chore.due_date or date.today(),
                    chore.recurrence_pattern,
                    chore.recurrence_interval
                ),
                next_occurrence=calculate_next_occurrence(
                    chore.next_occurrence or date.today(),
                    chore.recurrence_pattern,
                    chore.recurrence_interval
                )
            )
            session.add(next_chore)
        
        await session.commit()
        await session.refresh(completion)
        
        return completion, None
    
    @staticmethod
    async def update_overdue_status(session: AsyncSession) -> int:
        """Update status of overdue chores. Returns count of updated chores."""
        today = date.today()
        result = await session.execute(
            update(Chore)
            .where(
                and_(
                    Chore.due_date < today,
                    Chore.status.in_([ChoreStatus.PENDING, ChoreStatus.IN_PROGRESS]),
                    Chore.is_archived == False
                )
            )
            .values(status=ChoreStatus.OVERDUE)
        )
        await session.commit()
        return result.rowcount or 0