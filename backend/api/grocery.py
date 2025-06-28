"""
Grocery List API Router (Enhanced Version)

This module provides REST API endpoints for managing grocery lists using async SQLAlchemy and SQLite.
Includes automatic migration from the old JSON file on first run with improved error handling.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.exceptions import (DatabaseException, NotFoundException,
                               ValidationException)
from ..database import get_db
from ..models.grocery import GroceryItem
from ..models.schemas.grocery import GroceryItem as GroceryItemSchema
from ..models.schemas.grocery import (GroceryItemCreate, GroceryItemResponse,
                                      GroceryItemUpdate, GroceryListResponse)
from ..services.security import validate_file_path

# Configure logging
logger = logging.getLogger(__name__)

# Data migration from old JSON file
DATA_DIR = Path(__file__).parent.parent / "data"
GROCERY_JSON = DATA_DIR / "grocery_list.json"

async def migrate_json_to_db():
    """Migrate grocery items from JSON file to the database if DB is empty."""
    try:
        from ..database import get_db_session
        
        async with get_db_session() as session:
            result = await session.execute(select(GroceryItem))
            items = result.scalars().all()
            if items:
                logger.info("Database already contains grocery items, skipping migration")
                return  # DB already has data
            
            if GROCERY_JSON.exists():
                # Validate file path for security
                if not validate_file_path(str(GROCERY_JSON), [str(DATA_DIR)]):
                    logger.error("Invalid file path for grocery migration")
                    return
                
                with open(GROCERY_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("items", []):
                        db_item = GroceryItem(
                            name=item["name"],
                            quantity=item.get("quantity"),
                            category=item.get("category"),
                            notes=item.get("notes"),
                            priority=item.get("priority", "medium"),
                            completed=item.get("completed", False),
                            created_at=datetime.fromisoformat(item["created_at"]),
                            updated_at=datetime.fromisoformat(item["updated_at"]),
                        )
                        session.add(db_item)
                    await session.commit()
                
                # Rename the old JSON file
                GROCERY_JSON.rename(GROCERY_JSON.with_suffix(".migrated.json"))
                logger.info(f"Migrated {len(data.get('items', []))} grocery items from JSON to database")
            else:
                logger.info("No legacy grocery JSON file found, skipping migration")
    except Exception as e:
        logger.error(f"Error during grocery migration: {e}", exc_info=True)
        raise DatabaseException("Failed to migrate grocery data", operation="migration")

# Initialize router
grocery_router = APIRouter()

@grocery_router.on_event("startup")
async def on_startup():
    """Initialize database and run migration on startup."""
    from ..database import init_db
    await init_db()
    await migrate_json_to_db()

@grocery_router.get("/", response_model=GroceryListResponse)
async def get_grocery_list(
    request: Request,
    completed: Optional[bool] = None, 
    db: AsyncSession = Depends(get_db)
) -> GroceryListResponse:
    """
    Get all grocery items, optionally filtered by completion status.
    """
    try:
        stmt = select(GroceryItem)
        if completed is not None:
            stmt = stmt.where(GroceryItem.completed == completed)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        # Sort by priority (high to low) then by creation date (newest first)
        def priority_order(priority):
            return {"high": 3, "medium": 2, "low": 1}.get(priority, 2)
        
        items.sort(key=lambda x: (priority_order(x.priority), x.created_at), reverse=True)
        
        # Calculate counts
        total_count = await db.scalar(select(func.count()).select_from(GroceryItem))
        completed_count = await db.scalar(
            select(func.count()).select_from(GroceryItem).where(GroceryItem.completed == True)
        )
        pending_count = total_count - completed_count
        
        return GroceryListResponse(
            items=[GroceryItemSchema.model_validate(item) for item in items],
            total_count=total_count,
            completed_count=completed_count,
            pending_count=pending_count
        )
    except Exception as e:
        logger.error(f"Error getting grocery list: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve grocery list", operation="select")

@grocery_router.post("/", response_model=GroceryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_grocery_item(
    request: Request,
    item: GroceryItemCreate, 
    db: AsyncSession = Depends(get_db)
) -> GroceryItemResponse:
    """
    Create a new grocery item.
    """
    try:
        # Validate input
        if not item.name or not item.name.strip():
            raise ValidationException("Item name is required")
        
        if len(item.name.strip()) > 200:
            raise ValidationException("Item name is too long (max 200 characters)")
        
        now = datetime.utcnow()
        db_item = GroceryItem(
            name=item.name.strip(),
            quantity=item.quantity,
            category=item.category,
            notes=item.notes,
            priority=item.priority or "medium",
            completed=False,
            created_at=now,
            updated_at=now
        )
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        
        return GroceryItemResponse(
            item=GroceryItemSchema.model_validate(db_item),
            message="Grocery item created successfully"
        )
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error creating grocery item: {e}", exc_info=True)
        raise DatabaseException("Failed to create grocery item", operation="insert")

@grocery_router.get("/{item_id}", response_model=GroceryItemResponse)
async def get_grocery_item(
    request: Request,
    item_id: int, 
    db: AsyncSession = Depends(get_db)
) -> GroceryItemResponse:
    """
    Get a specific grocery item by ID.
    """
    try:
        result = await db.execute(select(GroceryItem).where(GroceryItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Grocery item", str(item_id))
        
        return GroceryItemResponse(
            item=GroceryItemSchema.model_validate(item),
            message="Grocery item retrieved successfully"
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting grocery item {item_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve grocery item", operation="select")

@grocery_router.put("/{item_id}", response_model=GroceryItemResponse)
async def update_grocery_item(
    request: Request,
    item_id: int, 
    item_update: GroceryItemUpdate, 
    db: AsyncSession = Depends(get_db)
) -> GroceryItemResponse:
    """
    Update an existing grocery item.
    """
    try:
        result = await db.execute(select(GroceryItem).where(GroceryItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Grocery item", str(item_id))
        
        update_data = item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(item)
        
        return GroceryItemResponse(
            item=GroceryItemSchema.model_validate(item),
            message="Grocery item updated successfully"
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating grocery item {item_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to update grocery item", operation="update")

@grocery_router.delete("/{item_id}")
async def delete_grocery_item(
    request: Request,
    item_id: int, 
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Delete a grocery item.
    """
    try:
        result = await db.execute(select(GroceryItem).where(GroceryItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Grocery item", str(item_id))
        
        await db.delete(item)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Grocery item with ID {item_id} deleted successfully"}
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting grocery item {item_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to delete grocery item", operation="delete")

@grocery_router.patch("/{item_id}/toggle", response_model=GroceryItemResponse)
async def toggle_grocery_item(
    request: Request,
    item_id: int, 
    db: AsyncSession = Depends(get_db)
) -> GroceryItemResponse:
    """
    Toggle the completion status of a grocery item.
    """
    try:
        result = await db.execute(select(GroceryItem).where(GroceryItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Grocery item", str(item_id))
        
        item.completed = not item.completed
        item.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(item)
        
        status_text = "completed" if item.completed else "marked as pending"
        return GroceryItemResponse(
            item=GroceryItemSchema.model_validate(item),
            message=f"Grocery item {status_text} successfully"
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error toggling grocery item {item_id}: {e}", exc_info=True)
        raise DatabaseException("Failed to toggle grocery item", operation="update")

@grocery_router.delete("/", status_code=status.HTTP_200_OK)
async def clear_completed_items(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Remove all completed grocery items from the list.
    """
    try:
        result = await db.execute(select(GroceryItem).where(GroceryItem.completed == True))
        items = result.scalars().all()
        removed_count = len(items)
        
        for item in items:
            await db.delete(item)
        await db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Cleared {removed_count} completed items",
                "removed_count": removed_count
            }
        )
    except Exception as e:
        logger.error(f"Error clearing completed items: {e}", exc_info=True)
        raise DatabaseException("Failed to clear completed items", operation="delete") 