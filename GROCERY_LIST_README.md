# Grocery List Feature

A comprehensive grocery list management system integrated into the family dashboard.

## Features

- ✅ **Add Items**: Add grocery items with name, quantity, category, priority, and notes
- ✅ **Edit Items**: Inline editing of existing items
- ✅ **Delete Items**: Remove items from the list
- ✅ **Toggle Completion**: Mark items as completed/pending
- ✅ **Priority Levels**: Low, Medium, High priority with color coding
- ✅ **Categories**: Predefined categories for easy organization
- ✅ **Clear Completed**: Bulk remove completed items
- ✅ **Persistent Storage**: Data saved to SQLite database (dashboard.db) using async SQLAlchemy
- ✅ **Automatic Migration**: Legacy JSON data is migrated to the database on first run
- ✅ **Real-time Updates**: Automatic refresh after operations
- ✅ **Improved UX**: Compact list, empty state with Add button, full-featured expanded view

## Backend API Endpoints

The grocery list API is available at `http://localhost:8000/api/grocery/`:

- `GET /api/grocery/` - Get all grocery items
- `POST /api/grocery/` - Add new grocery item
- `GET /api/grocery/{item_id}` - Get specific item
- `PUT /api/grocery/{item_id}` - Update item
- `DELETE /api/grocery/{item_id}` - Delete item
- `PATCH /api/grocery/{item_id}/toggle` - Toggle completion status
- `DELETE /api/grocery/` - Clear all completed items

## Data Structure

### Grocery Item

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

## Usage

1. **Start the Backend Server**:

   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   - On first run, any legacy grocery data in `backend/data/grocery_list.json` will be migrated to the database (`backend/data/dashboard.db`).

2. **Start the Frontend Development Server**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Dashboard**:
   - Open `http://localhost:5173` in your browser
   - Click on the "Grocery List" quadrant to expand it
   - Use the "Add Item" button to add new grocery items

## Components

### Main Components

- `GroceryList.svelte` - Main grocery list component (compact and expanded views)
- `AddItemForm.svelte` - Form for adding new items
- `GroceryItemCard.svelte` - Individual item display and editing

### Store

- `grocery.ts` - Svelte store for state management and API calls

## File Structure

```
backend/
├── api/
│   └── grocery.py          # API endpoints (async SQLAlchemy)
├── schemas/
│   └── grocery.py          # Pydantic models
├── models.py               # SQLAlchemy ORM models and async DB setup
└── data/
    ├── dashboard.db        # SQLite database (all grocery data)
    └── grocery_list.json.migrated.json   # Legacy data (after migration)

frontend/
└── src/
    └── lib/
        ├── components/
        │   ├── GroceryList.svelte
        │   └── grocery/
        │       ├── AddItemForm.svelte
        │       └── GroceryItemCard.svelte
        └── stores/
            └── grocery.ts
```

## Priority Colors

- **Low**: Green (text-green-600 bg-green-100)
- **Medium**: Yellow (text-yellow-600 bg-yellow-100)
- **High**: Red (text-red-600 bg-red-100)

## Categories

Predefined categories include:

- Produce
- Dairy
- Meat
- Pantry
- Frozen
- Beverages
- Snacks
- Household
- Personal Care

## Data Persistence

Grocery items are stored in `backend/data/dashboard.db` (SQLite) and persist between server restarts. Legacy data is auto-migrated from `grocery_list.json` on first run.

## Error Handling

The system includes comprehensive error handling:

- Form validation with user-friendly error messages
- API error handling with retry mechanisms
- Loading states for better UX
- Confirmation dialogs for destructive actions

## Improved UX

- **Compact List:** Simple, fast overview in dashboard mode
- **Empty State:** Friendly message and "Add Item" button when list is empty
- **Expanded View:** Full-featured add/edit/delete, priority, category, and notes

## Future Enhancements

Potential improvements:

- Shopping list templates
- Barcode scanning
- Price tracking
- Shopping history
- Family member assignments
- Integration with grocery store APIs
- Mobile app support
