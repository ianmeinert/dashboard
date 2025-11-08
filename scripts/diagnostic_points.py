"""
Dashboard Points Diagnostic Script (Windows Compatible)
Check historical completion data and member points to diagnose weekly reset issues

Run with: python diagnose_points.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# Database URL - Update this to match your database location
ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{os.getenv('DATABASE_URL').split(':///')[-1]}"

async def check_member_points_status():
    """Check current member points and last reset dates"""
    print("🔍 MEMBER POINTS STATUS CHECK")
    print("=" * 60)
    
    engine = create_async_engine(ASYNC_DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Get all members with their points
        result = await session.execute(text("""
            SELECT 
                fm.id,
                fm.name,
                fm.total_points,
                fm.monthly_points,
                fm.weekly_points,
                fm.weekly_points_cap,
                fm.last_weekly_reset,
                fm.last_monthly_reset,
                ag.name as age_group_name
            FROM family_members fm
            LEFT JOIN age_groups ag ON fm.age_group_id = ag.id
            WHERE fm.is_active = 1
            ORDER BY fm.name
        """))
        
        members = result.fetchall()
        
        if not members:
            print("❌ No family members found in database")
            return
        
        current_date = datetime.now().date()
        days_since_monday = current_date.weekday()
        current_week_start = current_date - timedelta(days=days_since_monday)
        
        print(f"Current Date: {current_date}")
        print(f"Current Week Start (Monday): {current_week_start}")
        print()
        
        for member in members:
            print(f"👤 {member.name} ({member.age_group_name or 'No age group'})")
            print(f"   Total Points: {member.total_points}")
            print(f"   Monthly Points: {member.monthly_points}")
            print(f"   Weekly Points: {member.weekly_points}/{member.weekly_points_cap}")
            
            if member.last_weekly_reset:
                last_reset = datetime.strptime(str(member.last_weekly_reset), '%Y-%m-%d').date()
                days_since_reset = (current_date - last_reset).days
                needs_reset = last_reset < current_week_start
                
                print(f"   Last Weekly Reset: {last_reset} ({days_since_reset} days ago)")
                print(f"   ⚠️  NEEDS RESET: {needs_reset}")
                
                if needs_reset:
                    print(f"   🚨 Weekly points should have been reset on {current_week_start}")
            else:
                print(f"   Last Weekly Reset: Never")
                print(f"   🚨 NEEDS INITIAL RESET")
            
            print()

async def check_completion_history():
    """Check recent completion history by week"""
    print("📈 COMPLETION HISTORY BY WEEK")
    print("=" * 60)
    
    engine = create_async_engine(ASYNC_DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Get completions from last 4 weeks
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        
        result = await session.execute(text("""
            SELECT 
                cc.completed_at,
                cc.points_earned,
                cc.chore_title_snapshot,
                fm.name as member_name,
                cc.completed_by_id
            FROM chore_completions cc
            JOIN family_members fm ON cc.completed_by_id = fm.id
            WHERE cc.completed_at >= :start_date
            ORDER BY cc.completed_at DESC
        """), {'start_date': four_weeks_ago})
        
        completions = result.fetchall()
        
        if not completions:
            print("❌ No completion history found")
            return
        
        print(f"Found {len(completions)} completions in the last 4 weeks")
        print()
        
        # Group by member and week
        weekly_summary = {}
        
        for completion in completions:
            completed_at = datetime.fromisoformat(str(completion.completed_at))
            member_name = completion.member_name
            points = completion.points_earned
            
            # Calculate which week this belongs to (Monday = start of week)
            completed_date = completed_at.date()
            days_since_monday = completed_date.weekday()
            week_start = completed_date - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            week_key = f"{week_start} to {week_end}"
            
            if member_name not in weekly_summary:
                weekly_summary[member_name] = {}
            if week_key not in weekly_summary[member_name]:
                weekly_summary[member_name][week_key] = {
                    'points': 0,
                    'chores': 0,
                    'week_start': week_start
                }
            
            weekly_summary[member_name][week_key]['points'] += points
            weekly_summary[member_name][week_key]['chores'] += 1
        
        # Display summary by member
        for member_name, weeks in weekly_summary.items():
            print(f"👤 {member_name}:")
            # Sort weeks by date
            sorted_weeks = sorted(weeks.items(), key=lambda x: x[1]['week_start'], reverse=True)
            for week_range, data in sorted_weeks:
                print(f"   📅 {week_range}: {data['points']} points, {data['chores']} chores")
            print()

async def check_weekly_archives():
    """Check if weekly archives exist"""
    print("📚 WEEKLY ARCHIVES CHECK")
    print("=" * 60)
    
    engine = create_async_engine(ASYNC_DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(text("""
            SELECT 
                wpa.week_start_date,
                wpa.week_end_date,
                wpa.points_earned,
                wpa.weekly_cap,
                wpa.chores_completed,
                fm.name as member_name
            FROM weekly_points_archive wpa
            JOIN family_members fm ON wpa.family_member_id = fm.id
            ORDER BY wpa.week_start_date DESC, fm.name
            LIMIT 20
        """))
        
        archives = result.fetchall()
        
        if not archives:
            print("❌ No weekly archives found - this indicates weekly resets have never run")
            return
        
        print(f"Found {len(archives)} archived weeks (showing most recent 20)")
        print()
        
        current_member = None
        for archive in archives:
            if archive.member_name != current_member:
                current_member = archive.member_name
                print(f"👤 {current_member}:")
            
            utilization = (archive.points_earned / archive.weekly_cap * 100) if archive.weekly_cap > 0 else 0
            print(f"   📅 {archive.week_start_date} to {archive.week_end_date}: "
                  f"{archive.points_earned}/{archive.weekly_cap} points ({utilization:.1f}%), "
                  f"{archive.chores_completed} chores")

async def recommend_actions():
    """Provide recommendations based on findings"""
    print("💡 RECOMMENDATIONS")
    print("=" * 60)
    
    engine = create_async_engine(ASYNC_DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Check if any member has weekly_points > 0 and old last_weekly_reset
        result = await session.execute(text("""
            SELECT COUNT(*) as needs_reset_count
            FROM family_members 
            WHERE weekly_points > 0 
            AND (
                last_weekly_reset IS NULL 
                OR last_weekly_reset < date('now', '-7 days')
            )
        """))
        
        needs_reset = result.scalar()
        
        # Check for archives
        archive_result = await session.execute(text("""
            SELECT COUNT(*) as archive_count
            FROM weekly_points_archive
        """))
        
        archive_count = archive_result.scalar()
        
        print("Based on the diagnostic results:")
        print()
        
        if needs_reset > 0:
            print(f"🚨 URGENT: {needs_reset} member(s) need weekly points reset")
            print("   Action: Run manual weekly reset endpoint or implement automatic reset")
            print("   Endpoint: POST /api/chores/admin/reset-weekly")
            print()
        
        if archive_count == 0:
            print("⚠️  No weekly archives found")
            print("   This means weekly resets have never been run")
            print("   Points have been accumulating since system start")
            print()
        
        print("🔧 FIXES NEEDED:")
        print("1. Implement automatic weekly reset in member retrieval endpoints")
        print("2. Add background scheduler (celery/APScheduler) to run weekly resets")
        print("3. Add monitoring to track reset success/failures")
        print("4. Consider adding a 'force reset all' admin endpoint")
        print()
        
        print("🚀 IMMEDIATE ACTIONS:")
        print("1. Run manual reset: curl -X POST http://localhost:8000/api/chores/admin/reset-weekly")
        print("2. Update the API code with the automatic reset logic provided")
        print("3. Deploy the fixed version")
        print("4. Monitor weekly resets going forward")

async def main():
    """Run all diagnostic checks"""
    print("🏠 FAMILY DASHBOARD CHORES - POINTS DIAGNOSTIC")
    print("=" * 80)
    print(f"Diagnostic run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        await check_member_points_status()
        print()
        await check_completion_history()
        print()
        await check_weekly_archives()
        print()
        await recommend_actions()
        
    except Exception as e:
        print(f"❌ Error running diagnostics: {e}")
        print("Make sure:")
        print("1. Database file exists and is accessible")
        print("2. Database URL is correct in the script")
        print("3. You have the required packages: sqlalchemy, aiosqlite, pandas")

if __name__ == "__main__":
    asyncio.run(main())