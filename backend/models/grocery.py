"""
GroceryItem SQLAlchemy ORM model

Defines the GroceryItem table for the grocery list feature.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .base import Base


class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    priority = Column(String(10), nullable=False, default="medium")
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow) 