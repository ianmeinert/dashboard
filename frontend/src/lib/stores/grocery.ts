/**
 * Grocery List Store
 * 
 * Manages grocery list state and API interactions using Svelte stores.
 */

import { derived, writable } from 'svelte/store';
import { serviceApi } from '../utils/api.js';

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

// Store methods
export const groceryStore = {
  subscribe,
  
  // Load all grocery items
  loadItems: async () => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.grocery.get();
      const data: GroceryListResponse = response.data;
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
      await serviceApi.grocery.post(item);
      
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
      await serviceApi.grocery.patch(itemId, {});
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
      await serviceApi.grocery.put(itemId, updates);
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
      await serviceApi.grocery.delete(itemId);
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
      await serviceApi.grocery.delete('/completed');
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

// Derived stores for computed values
export const groceryItems = derived(groceryStore, ($store) => $store.items);
export const groceryLoading = derived(groceryStore, ($store) => $store.loading);
export const groceryError = derived(groceryStore, ($store) => $store.error);
export const groceryStats = derived(groceryStore, ($store) => ({
  total: $store.total_count,
  completed: $store.completed_count,
  pending: $store.pending_count
}));

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