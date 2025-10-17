"""
Grocery List Schemas

This module defines Pydantic models for grocery list data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GroceryItemBase(BaseModel):
    """Base model for grocery item data."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the grocery item")
    quantity: Optional[str] = Field(None, max_length=50, description="Quantity of the item (e.g., '2 lbs', '1 dozen')")
    category: Optional[str] = Field(None, max_length=50, description="Category of the item (e.g., 'Produce', 'Dairy')")
    notes: Optional[str] = Field(None, max_length=200, description="Additional notes about the item")
    priority: Optional[str] = Field("medium", description="Priority level: low, medium, high")


class GroceryItemCreate(GroceryItemBase):
    """Model for creating a new grocery item."""
    pass


class GroceryItemUpdate(BaseModel):
    """Model for updating an existing grocery item."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)
    priority: Optional[str] = Field(None)
    completed: Optional[bool] = Field(None)


class GroceryItem(GroceryItemBase):
    """Complete grocery item model with database fields."""
    id: int = Field(..., description="Unique identifier for the grocery item")
    completed: bool = Field(False, description="Whether the item has been purchased")
    created_at: datetime = Field(..., description="When the item was added to the list")
    updated_at: datetime = Field(..., description="When the item was last modified")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class GroceryListResponse(BaseModel):
    """Response model for grocery list operations."""
    items: list[GroceryItem] = Field(..., description="List of grocery items")
    total_count: int = Field(..., description="Total number of items in the list")
    completed_count: int = Field(..., description="Number of completed items")
    pending_count: int = Field(..., description="Number of pending items")


class GroceryItemResponse(BaseModel):
    """Response model for single grocery item operations."""
    item: GroceryItem = Field(..., description="The grocery item")
    message: str = Field(..., description="Operation result message") 