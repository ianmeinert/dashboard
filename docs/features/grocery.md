# Grocery List Feature

A comprehensive grocery list management system integrated into the family dashboard with modern database storage and intuitive user interface.

## 🛒 Overview

The grocery list feature provides a complete shopping management solution with:

- **Smart item management** - Add, edit, delete, and check off items
- **Organization tools** - Categories, priorities, and notes
- **Database storage** - Robust SQLite backend with async SQLAlchemy
- **Auto-migration** - Seamless upgrade from legacy JSON storage
- **Responsive design** - Works on desktop, tablet, and mobile

## ✨ Features

### Core Functionality

- ✅ **Add Items** - Add grocery items with name, quantity, category, priority, and notes
- ✅ **Edit Items** - Inline editing of existing items
- ✅ **Delete Items** - Remove items from the list
- ✅ **Toggle Completion** - Mark items as completed/pending
- ✅ **Priority Levels** - Low, Medium, High priority with color coding
- ✅ **Categories** - Predefined categories for easy organization
- ✅ **Clear Completed** - Bulk remove completed items
- ✅ **Persistent Storage** - Data saved to SQLite database using async SQLAlchemy
- ✅ **Auto-Migration** - Legacy JSON data migrated to database on first run
- ✅ **Real-time Updates** - Automatic refresh after operations
- ✅ **Improved UX** - Compact list, empty state, full-featured expanded view

### User Experience

- **Compact Dashboard View** - Quick overview in the main dashboard
- **Expanded Management View** - Full-featured interface for detailed management
- **Empty State** - Friendly message with "Add Item" button when list is empty
- **Error Handling** - User-friendly error messages and validation
- **Loading States** - Visual feedback during operations

## 🏗️ Architecture

### Backend Components

```
backend/
├── api/
│   └── grocery.py          # API endpoints (async SQLAlchemy)
├── schemas/
│   └── grocery.py          # Pydantic models for validation
├── models.py               # SQLAlchemy ORM models and async DB setup
└── data/
    ├── dashboard.db        # SQLite database (all grocery data)
    └── grocery_list.json.migrated.json   # Legacy data (after migration)
```

### Frontend Components

```
frontend/
└── src/
    └── lib/
        ├── components/
        │   ├── GroceryList.svelte        # Main grocery list component
        │   └── grocery/
        │       ├── AddItemForm.svelte    # Form for adding new items
        │       └── GroceryItemCard.svelte # Individual item display/editing
        └── stores/
            └── grocery.ts                # Svelte store for state management
```

## 📊 Data Model

### Grocery Item Structure

```typescript
interface GroceryItem {
  id: number;
  name: string;
  quantity?: string;
  category?: string;
  notes?: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  created_at: string;
  updated_at: string;
}
```

### Create Item Request

```typescript
interface GroceryItemCreate {
  name: string;
  quantity?: string;
  category?: string;
  notes?: string;
  priority?: 'low' | 'medium' | 'high';
}
```

## 🔌 API Endpoints

The grocery list API is available at `http://localhost:8000/api/grocery/`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/grocery/` | Get all grocery items |
| `POST` | `/api/grocery/` | Add new grocery item |
| `GET` | `/api/grocery/{item_id}` | Get specific item |
| `PUT` | `/api/grocery/{item_id}` | Update item |
| `DELETE` | `/api/grocery/{item_id}` | Delete item |
| `PATCH` | `/api/grocery/{item_id}/toggle` | Toggle completion status |
| `DELETE` | `/api/grocery/` | Clear all completed items |

### Example API Usage

```bash
# Get all items
curl http://localhost:8000/api/grocery/

# Add new item
curl -X POST http://localhost:8000/api/grocery/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bananas", "quantity": "2 lbs", "category": "Produce", "priority": "medium"}'

# Toggle completion
curl -X PATCH http://localhost:8000/api/grocery/1/toggle

# Clear completed items
curl -X DELETE http://localhost:8000/api/grocery/
```

## 🎨 User Interface

### Dashboard View (Compact)

The grocery list appears as a compact widget in the main dashboard:

- Shows top 5 items by priority
- Displays completion status with checkboxes
- Priority badges with color coding
- "View All" button to expand

### Expanded View (Full Management)

Click the grocery quadrant to access the full management interface:

- Complete list of all items
- Add new item form
- Inline editing capabilities
- Category and priority filters
- Bulk actions (clear completed)

### Priority Colors

- **Low Priority**: Green (`text-green-600 bg-green-100`)
- **Medium Priority**: Yellow (`text-yellow-600 bg-yellow-100`)
- **High Priority**: Red (`text-red-600 bg-red-100`)

### Categories

Predefined categories for easy organization:

- Produce
- Dairy
- Meat
- Pantry
- Frozen
- Beverages
- Snacks
- Household
- Personal Care

## 💾 Data Storage

### Database Schema

```sql
CREATE TABLE grocery_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity TEXT,
    category TEXT,
    notes TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migration Process

On first run, the system automatically migrates legacy data:

1. **Check for legacy file** - Looks for `grocery_list.json`
2. **Backup legacy data** - Creates `grocery_list.json.migrated.json`
3. **Import to database** - Transfers all items to SQLite
4. **Verify migration** - Ensures data integrity
5. **Log results** - Reports migration status

### Data Persistence

- **SQLite Database**: `backend/data/dashboard.db`
- **Automatic backups**: Legacy data preserved as `.migrated.json`
- **Transaction safety**: All operations use database transactions
- **Error recovery**: Graceful handling of database errors

## 🔧 Configuration

### Environment Variables

```env
# Database configuration
DATABASE_URL=sqlite:///./data/dashboard.db

# Grocery list settings
GROCERY_MAX_ITEMS=100
GROCERY_DEFAULT_PRIORITY=medium
```

### Default Settings

- **Default Priority**: Medium
- **Max Items**: 100 (configurable)
- **Auto-refresh**: 30 seconds
- **Categories**: 9 predefined categories

## 🚀 Usage Guide

### Getting Started

1. **Start the Backend Server**:

   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Dashboard**:
   - Open `http://localhost:5173`
   - Click on the "Grocery List" quadrant to expand
   - Use the "Add Item" button to add new items

### Adding Items

1. Click "Add Item" button
2. Fill in the form:
   - **Name** (required): Item name
   - **Quantity** (optional): Amount needed
   - **Category** (optional): Select from dropdown
   - **Priority** (optional): Low, Medium, or High
   - **Notes** (optional): Additional information
3. Click "Add Item" to save

### Managing Items

- **Edit**: Click the edit icon on any item
- **Toggle**: Click the checkbox to mark complete/incomplete
- **Delete**: Click the delete icon to remove an item
- **Clear Completed**: Use the "Clear Completed" button for bulk removal

### Organization Tips

- **Use categories** to group similar items
- **Set priorities** for urgent items
- **Add notes** for specific requirements
- **Check off items** as you shop
- **Clear completed** to keep the list tidy

## 🐛 Troubleshooting

### Common Issues

**Items not saving:**

- Check backend server is running
- Verify database file permissions
- Check browser console for errors

**Migration not working:**

- Ensure legacy JSON file exists
- Check database file permissions
- Review backend logs for errors

**UI not updating:**

- Refresh the page
- Check network connectivity
- Verify API endpoints are accessible

### Error Messages

- **"Item name is required"** - Name field cannot be empty
- **"Priority must be low, medium, or high"** - Invalid priority value
- **"Failed to save item"** - Database or network error
- **"Item not found"** - Item was deleted or doesn't exist

## 🔮 Future Enhancements

### Planned Features

- **Shopping list templates** - Save common shopping lists
- **Barcode scanning** - Scan items to add automatically
- **Price tracking** - Track prices across stores
- **Shopping history** - View past shopping trips
- **Family member assignments** - Assign items to family members
- **Integration with grocery store APIs** - Real-time inventory and pricing
- **Mobile app support** - Native mobile applications

### Enhancement Ideas

- **Recipe integration** - Add ingredients from recipes
- **Expiration tracking** - Track food expiration dates
- **Nutritional information** - Display nutritional data
- **Shopping list sharing** - Share lists with family members
- **Voice input** - Add items using voice commands
- **Smart suggestions** - AI-powered item suggestions

## 📚 Related Documentation

- **[Backend API](../api-reference.md)** - Complete API documentation
- **[Database Schema](../database-schema.md)** - Data models and relationships
- **[Configuration Guide](../configuration.md)** - Environment setup
- **[Development Guide](../development.md)** - Contributing to the project

---

**Need help?** Check the [Troubleshooting Guide](../troubleshooting.md) or open an issue on GitHub.
