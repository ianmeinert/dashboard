"""
Chores Module - Initial Data Seeding
Seeds default age groups and optionally creates sample data for testing
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db_session, init_db
from backend.models.chores import AgeGroup, FamilyMember


async def seed_age_groups(session: AsyncSession) -> None:
    """
    Seed default age groups with weekly point caps.
    This is idempotent - safe to run multiple times.
    """
    
    # Define default age groups based on your family structure
    default_age_groups = [
        {
            "name": "Young (5-10)",
            "min_age": 5,
            "max_age": 10,
            "default_weekly_cap": 25
        },
        {
            "name": "Teen (11-15)",
            "min_age": 11,
            "max_age": 15,
            "default_weekly_cap": 27
        },
        {
            "name": "Older Teen (16-17)",
            "min_age": 16,
            "max_age": 17,
            "default_weekly_cap": 30
        },
        {
            "name": "Adult (18+)",
            "min_age": 18,
            "max_age": 100,
            "default_weekly_cap": 30
        }
    ]
    
    print("🔄 Seeding age groups...")
    
    for group_data in default_age_groups:
        # Check if age group already exists
        result = await session.execute(
            select(AgeGroup).where(AgeGroup.name == group_data["name"])
        )
        existing_group = result.scalar_one_or_none()
        
        if existing_group:
            print(f"  ⏭️  Age group '{group_data['name']}' already exists, skipping...")
        else:
            age_group = AgeGroup(**group_data)
            session.add(age_group)
            print(f"  ✅ Created age group: {group_data['name']} ({group_data['default_weekly_cap']} pts/week)")
    
    await session.commit()
    print("✨ Age groups seeding complete!\n")


async def seed_sample_family_members(session: AsyncSession) -> None:
    """
    Optional: Seed sample family members for testing.
    Based on the real family members mentioned in the project plan:
    Seren, Torin (Young), Evlin (Teen), Aedan (custom cap)
    """
    
    print("🔄 Seeding sample family members...")
    
    # Get age groups
    result = await session.execute(select(AgeGroup))
    age_groups = result.scalars().all()
    age_group_map = {ag.name: ag for ag in age_groups}
    
    sample_members = [
        {
            "name": "Seren",
            "age": 10,
            "age_group_id": age_group_map.get("Young (5-10)").id if age_group_map.get("Young (5-10)") else None,
        },
        {
            "name": "Torin",
            "age": 10,
            "age_group_id": age_group_map.get("Young (5-10)").id if age_group_map.get("Young (5-10)") else None,
        },
        {
            "name": "Evlin",
            "age": 13,
            "age_group_id": age_group_map.get("Teen (11-15)").id if age_group_map.get("Teen (11-15)") else None,
        },
        {
            "name": "Aedan",
            "age": 16,
            "age_group_id": age_group_map.get("Older Teen (16-17)").id if age_group_map.get("Older Teen (16-17)") else None,
            "weekly_points_cap": 29  # Custom override as mentioned
        },
        {
            "name": "Ian",
            "age": 45,
            "age_group_id": age_group_map.get("Adult (18+)").id if age_group_map.get("Adult (18+)") else None,
        },
        {
            "name": "Cavan",
            "age": 19,
            "age_group_id": age_group_map.get("Adult (18+)").id if age_group_map.get("Adult (18+)") else None,
        },
        {
            "name": "Jade",
            "age": 22,
            "age_group_id": age_group_map.get("Adult (18+)").id if age_group_map.get("Adult (18+)") else None,
        }
    ]
    
    for member_data in sample_members:
        # Check if family member already exists
        result = await session.execute(
            select(FamilyMember).where(FamilyMember.name == member_data["name"])
        )
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            print(f"  ⏭️  Family member '{member_data['name']}' already exists, skipping...")
        else:
            family_member = FamilyMember(**member_data)
            session.add(family_member)
            cap_info = f" (custom cap: {member_data.get('weekly_points_cap')} pts)" if 'weekly_points_cap' in member_data else ""
            print(f"  ✅ Created family member: {member_data['name']}{cap_info}")
    
    await session.commit()
    print("✨ Sample family members seeding complete!\n")


async def run_seed(include_sample_data: bool = False) -> None:
    """
    Run the complete seeding process.
    
    Args:
        include_sample_data: If True, also seeds sample family members
    """
    print("\n" + "="*60)
    print("🌱 CHORES MODULE - DATABASE SEEDING")
    print("="*60 + "\n")
    
    try:
        # Initialize database tables
        print("📦 Initializing database tables...")
        await init_db()
        print("✅ Database tables initialized\n")
        
        # Seed age groups (always)
        async with get_db_session() as session:
            await seed_age_groups(session)
        
        # Optionally seed sample family members
        if include_sample_data:
            async with get_db_session() as session:
                await seed_sample_family_members(session)
        
        print("="*60)
        print("🎉 SEEDING COMPLETE!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise


async def reset_and_seed() -> None:
    """
    WARNING: This drops all tables and reseeds from scratch.
    Use only for development/testing!
    """
    from backend.database import engine
    from backend.models.base import Base
    
    print("\n⚠️  WARNING: This will drop all chores module tables!")
    print("Are you sure? This action cannot be undone.")
    
    # In production, you'd want proper confirmation
    # For now, this is just a utility function
    
    async with engine.begin() as conn:
        print("🗑️  Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tables dropped")
        
        print("📦 Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created\n")
    
    # Run seeding with sample data
    await run_seed(include_sample_data=True)


# CLI interface
if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    include_sample = "--sample" in sys.argv
    reset_mode = "--reset" in sys.argv
    
    if reset_mode:
        print("\n🔴 RESET MODE - All data will be lost!")
        asyncio.run(reset_and_seed())
    else:
        asyncio.run(run_seed(include_sample_data=include_sample))
        
        if not include_sample:
            print("💡 Tip: Run with --sample flag to also create sample family members")
            print("   Example: python -m backend.seed_chores --sample\n")