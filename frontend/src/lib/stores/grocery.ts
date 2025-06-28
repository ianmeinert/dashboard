/**
 * Grocery List Store
 * 
 * Manages grocery list state and API interactions using Svelte stores.
 */

import { derived, writable } from 'svelte/store';

// Types
export interface GroceryItem {
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

export interface GroceryListResponse {
  items: GroceryItem[];
  total_count: number;
  completed_count: number;
  pending_count: number;
}

export interface GroceryItemCreate {
  name: string;
  quantity?: string;
  category?: string;
  notes?: string;
  priority?: 'low' | 'medium' | 'high';
}

// Store state
interface GroceryStore {
  items: GroceryItem[];
  loading: boolean;
  error: string | null;
  total_count: number;
  completed_count: number;
  pending_count: number;
}

// Create the base store
const { subscribe, set, update } = writable<GroceryStore>({
  items: [],
  loading: false,
  error: null,
  total_count: 0,
  completed_count: 0,
  pending_count: 0
});

// API base URL
const API_BASE = 'http://localhost:8000/api/grocery';

// Helper function for API calls
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = {};
      }
      // Try to extract FastAPI validation error details
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // Validation error
          throw new Error(
            errorData.detail.map((d: any) => d.msg).join('; ')
          );
        }
        throw new Error(errorData.detail);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Store methods
export const groceryStore = {
  subscribe,
  
  // Load all grocery items
  loadItems: async () => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const data: GroceryListResponse = await apiCall('/');
      set({
        items: data.items,
        loading: false,
        error: null,
        total_count: data.total_count,
        completed_count: data.completed_count,
        pending_count: data.pending_count
      });
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load grocery items'
      }));
    }
  },

  // Add new grocery item
  addItem: async (item: GroceryItemCreate) => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      await apiCall('/', {
        method: 'POST',
        body: JSON.stringify(item)
      });
      
      // Reload the list to get the updated data
      await groceryStore.loadItems();
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to add grocery item'
      }));
    }
  },

  // Toggle item completion status
  toggleItem: async (itemId: number) => {
    try {
      await apiCall(`/${itemId}/toggle`, { method: 'PATCH' });
      await groceryStore.loadItems();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to toggle item'
      }));
    }
  },

  // Update grocery item
  updateItem: async (itemId: number, updates: Partial<GroceryItem>) => {
    try {
      await apiCall(`/${itemId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      });
      await groceryStore.loadItems();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to update item'
      }));
    }
  },

  // Delete grocery item
  deleteItem: async (itemId: number) => {
    try {
      await apiCall(`/${itemId}`, { method: 'DELETE' });
      await groceryStore.loadItems();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to delete item'
      }));
    }
  },

  // Clear completed items
  clearCompleted: async () => {
    try {
      await apiCall('/', { method: 'DELETE' });
      await groceryStore.loadItems();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to clear completed items'
      }));
    }
  },

  // Clear error
  clearError: () => {
    update(state => ({ ...state, error: null }));
  }
};

// Derived stores for filtered items
export const pendingItems = derived(groceryStore, ($store) => 
  $store.items.filter(item => !item.completed)
);

export const completedItems = derived(groceryStore, ($store) => 
  $store.items.filter(item => item.completed)
);

export const highPriorityItems = derived(groceryStore, ($store) => 
  $store.items.filter(item => item.priority === 'high' && !item.completed)
);

// Priority colors mapping
export const priorityColors = {
  low: 'text-green-600 bg-green-100',
  medium: 'text-yellow-600 bg-yellow-100',
  high: 'text-red-600 bg-red-100'
} as const;

// Priority labels
export const priorityLabels = {
  low: 'Low',
  medium: 'Medium',
  high: 'High'
} as const; 