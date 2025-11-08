/**
 * Chores Store
 * 
 * Manages chores, family members, and points tracking state using Svelte stores.
 */

import { derived, writable } from 'svelte/store';
import { serviceApi } from '../utils/api.js';

// ============================================================================
// Types
// ============================================================================

export type ChoreStatus = 'pending' | 'in_progress' | 'completed' | 'overdue';
export type ChorePriority = 'low' | 'medium' | 'high';
export type ChoreCategory = 
  | 'cleaning' 
  | 'cooking' 
  | 'dishes' 
  | 'laundry' 
  | 'trash' 
  | 'pets' 
  | 'yard' 
  | 'maintenance' 
  | 'organizing' 
  | 'other';

export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'biweekly' | 'monthly';

export interface Chore {
  id: number;
  title: string;
  description?: string;
  points: number;
  category: ChoreCategory;
  priority: ChorePriority;
  status: ChoreStatus;
  assigned_to_id?: number;
  assigned_to_name?: string;
  created_by_id: number;
  created_by_name: string;
  due_date?: string;
  next_due_date?: string;
  recurrence_type?: RecurrencePattern;
  recurrence_interval?: number;
  notes?: string;
  estimated_minutes?: number;
  created_at: string;
  updated_at: string;
}

export interface FamilyMember {
  id: number;
  name: string;
  age?: number;
  age_group_id?: number;
  age_group_name: string;
  total_points: number;
  weekly_points: number;
  weekly_points_cap: number;
  weekly_points_remaining: number;
  weekly_progress_percent: number;
  monthly_points: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgeGroup {
  id: number;
  name: string;
  min_age: number;
  max_age: number;
  default_weekly_cap: number;
  created_at: string;
  updated_at: string;
}

export interface ChoreCompletion {
  id: number;
  chore_id: number;
  completed_by_id: number;
  completed_by_name: string;
  chore_title_snapshot: string;
  points_earned: number;
  completed_at: string;
  completion_notes?: string;
  actual_minutes?: number;
  photo_url?: string;
}

export interface ChoreCreate {
  title: string;
  description?: string;
  points: number;
  category: ChoreCategory;
  priority?: ChorePriority;
  assigned_to_id?: number;
  created_by_id: number;
  due_date?: string;
  recurrence_type?: RecurrencePattern;
  recurrence_interval?: number;
  notes?: string;
  estimated_minutes?: number;
}

export interface ChoreUpdate {
  title?: string;
  description?: string;
  points?: number;
  category?: ChoreCategory;
  priority?: ChorePriority;
  assigned_to_id?: number;
  due_date?: string;
  recurrence_type?: RecurrencePattern;
  recurrence_interval?: number;
  notes?: string;
  estimated_minutes?: number;
  status?: ChoreStatus;
}

export interface ChoreCompletionCreate {
  chore_id: number;
  completed_by_id: number;
  completion_notes?: string;
  actual_minutes?: number;
  photo_url?: string;
}

export interface DashboardData {
  members: FamilyMember[];
  total_chores: number;
  pending_chores: number;
  completed_chores: number;
  completed_today: number;
}

// ============================================================================
// Store State
// ============================================================================

interface ChoresStoreState {
  chores: Chore[];
  members: FamilyMember[];
  ageGroups: AgeGroup[];
  completions: ChoreCompletion[];
  dashboardData: DashboardData | null;
  loading: boolean;
  error: string | null;
}

// Create the base store
const { subscribe, set, update } = writable<ChoresStoreState>({
  chores: [],
  members: [],
  ageGroups: [],
  completions: [],
  dashboardData: null,
  loading: false,
  error: null,
});

// ============================================================================
// Store Methods
// ============================================================================

export const choresStore = {
  subscribe,

  // ----------------------------------------------------------------------------
  // Dashboard
  // ----------------------------------------------------------------------------
  
  loadDashboard: async () => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.get('/dashboard');
      const data: DashboardData = response.data;
      
      update(state => ({
        ...state,
        dashboardData: data,
        members: data.members,
        loading: false,
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load dashboard',
      }));
    }
  },

  // ----------------------------------------------------------------------------
  // Chores
  // ----------------------------------------------------------------------------

  loadChores: async (filters?: { status?: ChoreStatus; assigned_to_id?: number }) => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      // First, ensure overdue status is up to date
      try {
        await serviceApi.chores.post({}, '/admin/update-overdue');
      } catch (error) {
        console.warn('Failed to update overdue status:', error);
        // Don't fail the entire load if this fails
      }
      
      let endpoint = '';
      const params = new URLSearchParams();
      
      if (filters?.status) params.append('status', filters.status);
      if (filters?.assigned_to_id) params.append('assigned_to_id', filters.assigned_to_id.toString());
      
      if (params.toString()) {
        endpoint = `?${params.toString()}`;
      }
      
      const response = await serviceApi.chores.get(endpoint);
      const chores: Chore[] = response.data;
      
      update(state => ({
        ...state,
        chores,
        loading: false,
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load chores',
      }));
    }
  },

  createChore: async (chore: ChoreCreate) => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      await serviceApi.chores.post(chore, '/');
      await choresStore.loadChores();
      await choresStore.loadDashboard();
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to create chore',
      }));
      throw error;
    }
  },

  updateChore: async (choreId: number, updates: ChoreUpdate) => {
    try {
      await serviceApi.chores.put(choreId, updates);
      await choresStore.loadChores();
      await choresStore.loadDashboard();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to update chore',
      }));
      throw error;
    }
  },

  deleteChore: async (choreId: number) => {
    try {
      await serviceApi.chores.delete(`/${choreId}`);
      await choresStore.loadChores();
      await choresStore.loadDashboard();
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to delete chore',
      }));
      throw error;
    }
  },

  // ----------------------------------------------------------------------------
  // Chore Completions
  // ----------------------------------------------------------------------------

  completeChore: async (completion: ChoreCompletionCreate) => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post(completion, '/completions');
      
      // Successfully completed - update local state and reload data
      update(state => ({ ...state, loading: false, error: null }));
      
      // Only reload the data we need - avoid redundant calls
      await Promise.all([
        choresStore.loadChores(),
        choresStore.loadMembers() // This updates the points display
      ]);
      
      return response; // Return response for success handling
    } catch (error) {
      // Reset loading state but DON'T set global error for validation failures
      // Let the UI component handle user-facing validation errors
      update(state => ({ ...state, loading: false, error: null }));
      
      // Still throw the error so the component can handle it
      throw error;
    }
  },

  loadCompletions: async (filters?: { completed_by_id?: number; chore_id?: number; limit?: number }) => {
    try {
      let endpoint = '/completions';
      const params = new URLSearchParams();
      
      if (filters?.completed_by_id) params.append('completed_by_id', filters.completed_by_id.toString());
      if (filters?.chore_id) params.append('chore_id', filters.chore_id.toString());
      if (filters?.limit) params.append('limit', filters.limit.toString());
      
      if (params.toString()) {
        endpoint += `?${params.toString()}`;
      }
      
      const response = await serviceApi.chores.get(endpoint);
      const completions: ChoreCompletion[] = response.data;
      
      update(state => ({
        ...state,
        completions,
      }));
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to load completions',
      }));
    }
  },

  // ----------------------------------------------------------------------------
  // Family Members
  // ----------------------------------------------------------------------------

  loadMembers: async () => {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.get('/members');
      const members: FamilyMember[] = response.data;
      
      update(state => ({
        ...state,
        members,
        loading: false,
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load members',
      }));
    }
  },

  // ----------------------------------------------------------------------------
  // Age Groups
  // ----------------------------------------------------------------------------

  loadAgeGroups: async () => {
    try {
      const response = await serviceApi.chores.get('/age-groups');
      const ageGroups: AgeGroup[] = response.data;
      
      update(state => ({
        ...state,
        ageGroups,
      }));
    } catch (error) {
      update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Failed to load age groups',
      }));
    }
  },

  // ----------------------------------------------------------------------------
  // Utility
  // ----------------------------------------------------------------------------

  clearError: () => {
    update(state => ({ ...state, error: null }));
  },
};

// ============================================================================
// Derived Stores
// ============================================================================

export const chores = derived(choresStore, ($store) => $store.chores);
export const members = derived(choresStore, ($store) => $store.members);
export const ageGroups = derived(choresStore, ($store) => $store.ageGroups);
export const completions = derived(choresStore, ($store) => $store.completions);
export const dashboardData = derived(choresStore, ($store) => $store.dashboardData);
export const choresLoading = derived(choresStore, ($store) => $store.loading);
export const choresError = derived(choresStore, ($store) => $store.error);

// Filtered chores
export const pendingChores = derived(choresStore, ($store) => 
  $store.chores.filter(chore => chore.status === 'pending')
);

export const completedChores = derived(choresStore, ($store) => 
  $store.chores.filter(chore => chore.status === 'completed')
);

export const overdueChores = derived(choresStore, ($store) => 
  $store.chores.filter(chore => chore.status === 'overdue')
);

export const highPriorityChores = derived(choresStore, ($store) => 
  $store.chores.filter(chore => chore.priority === 'high' && chore.status === 'pending')
);

// Category colors mapping
export const categoryColors: Record<ChoreCategory, string> = {
  cleaning: 'bg-blue-100 text-blue-800',
  cooking: 'bg-orange-100 text-orange-800',
  dishes: 'bg-cyan-100 text-cyan-800',
  laundry: 'bg-purple-100 text-purple-800',
  trash: 'bg-gray-100 text-gray-800',
  pets: 'bg-green-100 text-green-800',
  yard: 'bg-lime-100 text-lime-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  organizing: 'bg-pink-100 text-pink-800',
  other: 'bg-slate-100 text-slate-800',
};

// Priority colors mapping
export const priorityColors: Record<ChorePriority, string> = {
  low: 'text-green-600 bg-green-100',
  medium: 'text-yellow-600 bg-yellow-100',
  high: 'text-red-600 bg-red-100',
};

// Category labels
export const categoryLabels: Record<ChoreCategory, string> = {
  cleaning: 'Cleaning',
  cooking: 'Cooking',
  dishes: 'Dishes',
  laundry: 'Laundry',
  trash: 'Trash',
  pets: 'Pets',
  yard: 'Yard Work',
  maintenance: 'Maintenance',
  organizing: 'Organizing',
  other: 'Other',
};

// Priority labels
export const priorityLabels: Record<ChorePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
};
