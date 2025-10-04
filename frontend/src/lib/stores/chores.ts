/**
 * Family Chores Store
 * 
 * Manages family chore tracking state and API interactions using Svelte stores.
 * Handles parent authentication, household members, rooms, chores, and allowance calculations.
 */

import { derived, writable } from 'svelte/store';
import { serviceApi } from '../utils/api.js';

// Types
export interface Parent {
  id: number;
  name: string;
  pin: string; // Will be masked in responses
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface HouseholdMember {
  id: number;
  name: string;
  date_of_birth: string;
  is_parent: boolean;
  age: number;
  age_category: 'child' | 'preteen' | 'teenager' | 'adult';
  is_active: boolean;
  parent_id: number;
  created_at: string;
  updated_at: string;
}

export interface Room {
  id: number;
  name: string;
  description?: string;
  color_code?: string;
  is_active: boolean;
  parent_id: number;
  created_at: string;
  updated_at: string;
  chore_count?: number;
}

export interface Chore {
  id: number;
  name: string;
  description?: string;
  points: number;
  frequency: 'daily' | 'weekly' | 'monthly';
  is_active: boolean;
  room_id: number;
  parent_id: number;
  created_at: string;
  updated_at: string;
  last_completed_at?: string;
  next_available_at?: string;
  status?: 'pending' | 'completed' | 'disabled';
  completed_by?: string;
  room_name?: string;
}

export interface ChoreCompletion {
  id: number;
  chore_id: number;
  member_id: number;
  parent_id?: number;
  status: 'pending' | 'completed' | 'disabled';
  points_earned: number;
  completed_at?: string;
  confirmed_at?: string;
  week_start: string;
  created_at: string;
  member_name?: string;
  chore_name?: string;
}

export interface WeeklyPoints {
  id: number;
  member_id: number;
  week_start: string;
  week_end: string;
  points_earned: number;
  points_capped: number;
  member_name?: string;
}

export interface AllowanceCalculation {
  id: number;
  member_id: number;
  month_year: string;
  total_points_earned: number;
  total_points_possible: number;
  completion_percentage: number;
  allowance_amount: number;
  age_category: string;
  calculated_at: string;
  member_name?: string;
}

export interface ChoreDashboard {
  rooms: Room[];
  chores: Chore[];
  household_members: HouseholdMember[];
  pending_completions: ChoreCompletion[];
  weekly_points: WeeklyPoints[];
  current_member?: HouseholdMember;
}

export interface ParentDashboard {
  rooms: Room[];
  chores: Chore[];
  household_members: HouseholdMember[];
  pending_completions: ChoreCompletion[];
  weekly_points: WeeklyPoints[];
  allowance_calculations: AllowanceCalculation[];
}

// Create/Update types
export interface ParentCreate {
  name: string;
  pin: string;
}

export interface HouseholdMemberCreate {
  name: string;
  date_of_birth: string;
  is_parent?: boolean;
}

export interface HouseholdMemberUpdate {
  name?: string;
  date_of_birth?: string;
  is_parent?: boolean;
  is_active?: boolean;
}

export interface RoomCreate {
  name: string;
  description?: string;
  color_code?: string;
}

export interface RoomUpdate {
  name?: string;
  description?: string;
  color_code?: string;
  is_active?: boolean;
}

export interface ChoreCreate {
  name: string;
  description?: string;
  points: number;
  frequency: 'daily' | 'weekly' | 'monthly';
  room_id: number;
}

export interface ChoreUpdate {
  name?: string;
  description?: string;
  points?: number;
  frequency?: 'daily' | 'weekly' | 'monthly';
  is_active?: boolean;
}

export interface ChoreCompletionBatchConfirm {
  completion_ids: number[];
  confirmed: boolean;
}

export interface ChoreCompletionBatchResponse {
  processed_count: number;
  successful_count: number;
  failed_count: number;
  results: ChoreCompletion[];
  errors: any[];
}

export interface WeeklyPointsSummary {
  current_week_points: number;
  max_weekly_points: number;
  points_remaining: number;
  is_at_cap: boolean;
}

// Store state
interface ChoresStore {
  // Authentication
  currentParent: Parent | null;
  isAuthenticated: boolean;

  // Data
  rooms: Room[];
  chores: Chore[];
  householdMembers: HouseholdMember[];
  currentMember: HouseholdMember | null;
  pendingCompletions: ChoreCompletion[];
  weeklyPoints: WeeklyPoints[];
  allowanceCalculations: AllowanceCalculation[];

  // UI state
  loading: boolean;
  error: string | null;
  selectedRoomId: number | null;

  // Dashboard data
  dashboard: ChoreDashboard | null;
  parentDashboard: ParentDashboard | null;

  // SSE connection
  sseConnection: EventSource | null;
  isConnected: boolean;
}

// Create the base store
const { subscribe, set, update } = writable<ChoresStore>({
  currentParent: null,
  isAuthenticated: false,
  rooms: [],
  chores: [],
  householdMembers: [],
  currentMember: null,
  pendingCompletions: [],
  weeklyPoints: [],
  allowanceCalculations: [],
  loading: false,
  error: null,
  selectedRoomId: null,
  dashboard: null,
  parentDashboard: null,
  sseConnection: null,
  isConnected: false
});

// Store methods
export const choresStore = {
  subscribe,
  
  // Authentication
  async checkParentsExist(): Promise<{ exists: boolean; count: number }> {
    try {
      const response = await serviceApi.chores.get('/parents/exists');
      return response.data;
    } catch (error) {
      console.error('Failed to check if parents exist:', error);
      return { exists: false, count: 0 };
    }
  },

  async createParent(parentData: ParentCreate): Promise<Parent> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post('/parents', parentData);
      const parent: Parent = response.data;
      
      update(state => ({
        ...state,
        currentParent: parent,
        isAuthenticated: true,
        loading: false,
        error: null
      }));
      
      return parent;
    } catch (error) {
      let errorMessage = 'Failed to create parent';
      
      if (error instanceof Error) {
        // Check for specific error messages from the backend
        if (error.message.includes('already exists') || error.message.includes('duplicate')) {
          errorMessage = 'A parent with this name already exists. Please choose a different name.';
        } else if (error.message.includes('validation')) {
          errorMessage = 'Please check your input and try again.';
        } else {
          errorMessage = error.message;
        }
      }
      
      update(state => ({
        ...state,
        loading: false,
        error: errorMessage
      }));
      throw new Error(errorMessage);
    }
  },

  async verifyParent(name: string, pin: string): Promise<Parent> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      // Construct query string manually
      const queryParams = new URLSearchParams({ name, pin });
      const response = await serviceApi.chores.get(`/parents/verify?${queryParams.toString()}`);
      const parent: Parent = response.data;
      
      update(state => ({
        ...state,
        currentParent: parent,
        isAuthenticated: true,
        loading: false,
        error: null
      }));
      
      return parent;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to verify parent'
      }));
      throw error;
    }
  },

  logout(): void {
    // Close SSE connection before clearing state
    update(state => {
      if (state.sseConnection) {
        state.sseConnection.close();
      }
      return state;
    });

    set({
      currentParent: null,
      isAuthenticated: false,
      rooms: [],
      chores: [],
      householdMembers: [],
      currentMember: null,
      pendingCompletions: [],
      weeklyPoints: [],
      allowanceCalculations: [],
      loading: false,
      error: null,
      selectedRoomId: null,
      dashboard: null,
      parentDashboard: null,
      sseConnection: null,
      isConnected: false
    });
  },

  // SSE Real-time Updates
  connectToEventStream(parentId: number): void {
    // Close existing connection if any
    update(state => {
      if (state.sseConnection) {
        state.sseConnection.close();
      }
      return state;
    });

    try {
      const eventSource = new EventSource(`http://localhost:8000/api/chores/events/stream?parent_id=${parentId}`);

      eventSource.onopen = () => {
        console.log('SSE connection opened');
        update(state => ({ ...state, isConnected: true, error: null }));
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('SSE event received:', data);
          this.handleSSEEvent(data);
        } catch (error) {
          console.error('Failed to parse SSE event data:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        update(state => ({
          ...state,
          isConnected: false,
          error: 'Real-time connection lost. Please refresh the page if data seems outdated.'
        }));
      };

      // Store the connection
      update(state => ({ ...state, sseConnection: eventSource }));

    } catch (error) {
      console.error('Failed to establish SSE connection:', error);
      update(state => ({
        ...state,
        error: 'Failed to establish real-time connection',
        isConnected: false
      }));
    }
  },

  disconnectFromEventStream(): void {
    update(state => {
      if (state.sseConnection) {
        state.sseConnection.close();
      }
      return {
        ...state,
        sseConnection: null,
        isConnected: false
      };
    });
  },

  handleSSEEvent(eventData: any): void {
    const { event_type, data } = eventData;

    switch (event_type) {
      case 'chore_completed':
        this.handleChoreCompletedEvent(data);
        break;
      case 'completion_confirmed':
        this.handleCompletionConfirmedEvent(data);
        break;
      case 'completion_rejected':
        this.handleCompletionRejectedEvent(data);
        break;
      case 'chore_created':
        this.handleChoreCreatedEvent(data);
        break;
      case 'chore_updated':
        this.handleChoreUpdatedEvent(data);
        break;
      case 'room_created':
        this.handleRoomCreatedEvent(data);
        break;
      case 'room_updated':
        this.handleRoomUpdatedEvent(data);
        break;
      case 'member_created':
        this.handleMemberCreatedEvent(data);
        break;
      case 'member_updated':
        this.handleMemberUpdatedEvent(data);
        break;
      default:
        console.log('Unknown SSE event type:', event_type);
    }
  },

  handleChoreCompletedEvent(data: any): void {
    const completion: ChoreCompletion = data.completion;
    update(state => ({
      ...state,
      pendingCompletions: [...state.pendingCompletions, completion]
    }));
  },

  handleCompletionConfirmedEvent(data: any): void {
    const completionId = data.completion_id;
    update(state => ({
      ...state,
      pendingCompletions: state.pendingCompletions.filter(c => c.id !== completionId)
    }));
  },

  handleCompletionRejectedEvent(data: any): void {
    const completionId = data.completion_id;
    update(state => ({
      ...state,
      pendingCompletions: state.pendingCompletions.filter(c => c.id !== completionId)
    }));
  },

  handleChoreCreatedEvent(data: any): void {
    const chore: Chore = data.chore;
    update(state => ({
      ...state,
      chores: [...state.chores, chore]
    }));
  },

  handleChoreUpdatedEvent(data: any): void {
    const chore: Chore = data.chore;
    update(state => ({
      ...state,
      chores: state.chores.map(c => c.id === chore.id ? chore : c)
    }));
  },

  handleRoomCreatedEvent(data: any): void {
    const room: Room = data.room;
    update(state => ({
      ...state,
      rooms: [...state.rooms, room]
    }));
  },

  handleRoomUpdatedEvent(data: any): void {
    const room: Room = data.room;
    update(state => ({
      ...state,
      rooms: state.rooms.map(r => r.id === room.id ? room : r)
    }));
  },

  handleMemberCreatedEvent(data: any): void {
    const member: HouseholdMember = data.member;
    update(state => ({
      ...state,
      householdMembers: [...state.householdMembers, member]
    }));
  },

  handleMemberUpdatedEvent(data: any): void {
    const member: HouseholdMember = data.member;
    update(state => ({
      ...state,
      householdMembers: state.householdMembers.map(m => m.id === member.id ? member : m),
      currentMember: state.currentMember?.id === member.id ? member : state.currentMember
    }));
  },

  // Household Members
  async createHouseholdMember(memberData: HouseholdMemberCreate, parentId: number): Promise<HouseholdMember> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.post('/members', memberData, {
        params: { parent_id: parentId }
      });
      const member: HouseholdMember = response.data;

      update(state => ({
        ...state,
        householdMembers: [...state.householdMembers, member],
        loading: false,
        error: null
      }));

      return member;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to create household member'
      }));
      throw error;
    }
  },

  async updateHouseholdMember(memberId: number, memberData: HouseholdMemberUpdate): Promise<HouseholdMember> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.put(`/members/${memberId}`, memberData);
      const member: HouseholdMember = response.data;

      update(state => ({
        ...state,
        householdMembers: state.householdMembers.map(m => m.id === memberId ? member : m),
        // Update current member if it's the one being updated
        currentMember: state.currentMember?.id === memberId ? member : state.currentMember,
        loading: false,
        error: null
      }));

      return member;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to update household member'
      }));
      throw error;
    }
  },

  async loadHouseholdMembers(parentId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      // Construct query string manually
      const queryParams = new URLSearchParams({ parent_id: parentId.toString() });
      const response = await serviceApi.chores.get(`/members?${queryParams.toString()}`);
      const members: HouseholdMember[] = response.data;
      
      update(state => ({
        ...state,
        householdMembers: members,
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load household members'
      }));
    }
  },

  async loadAllHouseholdMembers(): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.get('/members/all');
      const members: HouseholdMember[] = response.data;

      update(state => ({
        ...state,
        householdMembers: members,
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load household members'
      }));
    }
  },

  async getMember(memberId: number): Promise<HouseholdMember> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.get(`/members/${memberId}`);
      const member: HouseholdMember = response.data;

      update(state => ({
        ...state,
        loading: false,
        error: null
      }));

      return member;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to get household member'
      }));
      throw error;
    }
  },

  setCurrentMember(member: HouseholdMember | null): void {
    update(state => ({ ...state, currentMember: member }));
  },

  // Rooms
  async createRoom(roomData: RoomCreate, parentId: number): Promise<Room> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post('/rooms', roomData, {
        params: { parent_id: parentId }
      });
      const room: Room = response.data;
      
      update(state => ({
        ...state,
        rooms: [...state.rooms, room],
        loading: false,
        error: null
      }));
      
      return room;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to create room'
      }));
      throw error;
    }
  },

  async loadRooms(parentId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.get('/rooms', {
        params: { parent_id: parentId }
      });
      const rooms: Room[] = response.data;
      
      update(state => ({
        ...state,
        rooms,
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load rooms'
      }));
    }
  },

  async updateRoom(roomId: number, roomData: RoomUpdate): Promise<Room> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.put(`/rooms/${roomId}`, roomData);
      const room: Room = response.data;
      
      update(state => ({
        ...state,
        rooms: state.rooms.map(r => r.id === roomId ? room : r),
        loading: false,
        error: null
      }));
      
      return room;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to update room'
      }));
      throw error;
    }
  },

  async deleteRoom(roomId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      await serviceApi.chores.delete(`/rooms/${roomId}`);
      
      update(state => ({
        ...state,
        rooms: state.rooms.filter(r => r.id !== roomId),
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to delete room'
      }));
      throw error;
    }
  },

  setSelectedRoom(roomId: number | null): void {
    update(state => ({ ...state, selectedRoomId: roomId }));
  },

  // Chores
  async createChore(choreData: ChoreCreate, parentId: number): Promise<Chore> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post('/chores', choreData, {
        params: { parent_id: parentId }
      });
      const chore: Chore = response.data;
      
      update(state => ({
        ...state,
        chores: [...state.chores, chore],
        loading: false,
        error: null
      }));
      
      return chore;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to create chore'
      }));
      throw error;
    }
  },

  async loadChores(parentId: number, roomId?: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const params: any = { parent_id: parentId };
      if (roomId) params.room_id = roomId;
      
      const response = await serviceApi.chores.get('/chores', { params });
      const chores: Chore[] = response.data;
      
      update(state => ({
        ...state,
        chores,
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load chores'
      }));
    }
  },

  async updateChore(choreId: number, choreData: ChoreUpdate): Promise<Chore> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.put(`/chores/${choreId}`, choreData);
      const chore: Chore = response.data;
      
      update(state => ({
        ...state,
        chores: state.chores.map(c => c.id === choreId ? chore : c),
        loading: false,
        error: null
      }));
      
      return chore;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to update chore'
      }));
      throw error;
    }
  },

  async deleteChore(choreId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      await serviceApi.chores.delete(`/chores/${choreId}`);
      
      update(state => ({
        ...state,
        chores: state.chores.filter(c => c.id !== choreId),
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to delete chore'
      }));
      throw error;
    }
  },

  // Chore Completions
  async completeChore(choreId: number, memberId: number): Promise<ChoreCompletion> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post(`/chores/${choreId}/complete`, null, {
        params: { member_id: memberId }
      });
      const completion: ChoreCompletion = response.data;
      
      update(state => ({
        ...state,
        pendingCompletions: [...state.pendingCompletions, completion],
        loading: false,
        error: null
      }));
      
      return completion;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to complete chore'
      }));
      throw error;
    }
  },

  async confirmChoreCompletion(completionId: number, parentId: number): Promise<ChoreCompletion> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.post(`/completions/${completionId}/confirm`, null, {
        params: { parent_id: parentId }
      });
      const completion: ChoreCompletion = response.data;
      
      update(state => ({
        ...state,
        pendingCompletions: state.pendingCompletions.filter(c => c.id !== completionId),
        loading: false,
        error: null
      }));
      
      return completion;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to confirm completion'
      }));
      throw error;
    }
  },

  async loadPendingCompletions(parentId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.get('/completions/pending', {
        params: { parent_id: parentId }
      });
      const completions: ChoreCompletion[] = response.data;

      update(state => ({
        ...state,
        pendingCompletions: completions,
        loading: false,
        error: null
      }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load pending completions'
      }));
    }
  },

  async getCompletions(
    parentId: number,
    filters?: {
      memberId?: number;
      status?: string;
      roomId?: number;
      sortBy?: string;
      sortOrder?: string;
    }
  ): Promise<ChoreCompletion[]> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const params: any = { parent_id: parentId };
      if (filters?.memberId) params.member_id = filters.memberId;
      if (filters?.status) params.status = filters.status;
      if (filters?.roomId) params.room_id = filters.roomId;
      if (filters?.sortBy) params.sort_by = filters.sortBy;
      if (filters?.sortOrder) params.sort_order = filters.sortOrder;

      const response = await serviceApi.chores.get('/completions', { params });
      const completions: ChoreCompletion[] = response.data;

      update(state => ({
        ...state,
        loading: false,
        error: null
      }));

      return completions;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load completions'
      }));
      throw error;
    }
  },

  async batchConfirmCompletions(
    batchData: ChoreCompletionBatchConfirm,
    parentId: number
  ): Promise<ChoreCompletionBatchResponse> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.post('/completions/batch-confirm', batchData, {
        params: { parent_id: parentId }
      });
      const batchResponse: ChoreCompletionBatchResponse = response.data;

      // Update pending completions by removing confirmed/rejected ones
      update(state => ({
        ...state,
        pendingCompletions: state.pendingCompletions.filter(
          completion => !batchData.completion_ids.includes(completion.id)
        ),
        loading: false,
        error: null
      }));

      return batchResponse;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to batch confirm completions'
      }));
      throw error;
    }
  },

  // Dashboard
  async loadDashboard(parentId: number, memberId?: number): Promise<ChoreDashboard> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const params: any = { parent_id: parentId };
      if (memberId) params.member_id = memberId;
      
      const response = await serviceApi.chores.get('/dashboard', { params });
      const dashboard: ChoreDashboard = response.data;
      
      update(state => ({
        ...state,
        dashboard,
        loading: false,
        error: null
      }));
      
      return dashboard;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load dashboard'
      }));
      throw error;
    }
  },

  // Allowance
  async calculateAllowance(memberId: number, monthYear: string): Promise<AllowanceCalculation> {
    update(state => ({ ...state, loading: true, error: null }));
    
    try {
      const response = await serviceApi.chores.get(`/allowance/${memberId}/${monthYear}`);
      const calculation: AllowanceCalculation = response.data;
      
      update(state => ({
        ...state,
        allowanceCalculations: state.allowanceCalculations.filter(c => 
          !(c.member_id === memberId && c.month_year === monthYear)
        ).concat(calculation),
        loading: false,
        error: null
      }));
      
      return calculation;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to calculate allowance'
      }));
      throw error;
    }
  },

  async getWeeklyStatus(memberId: number): Promise<WeeklyPointsSummary> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      const response = await serviceApi.chores.get(`/members/${memberId}/weekly-status`);
      const weeklyStatus: WeeklyPointsSummary = response.data;

      update(state => ({
        ...state,
        loading: false,
        error: null
      }));

      return weeklyStatus;
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to get weekly status'
      }));
      throw error;
    }
  },

  // Utility methods
  clearError(): void {
    update(state => ({ ...state, error: null }));
  },

  // Initialize data for a parent
  async initializeParentData(parentId: number): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      await Promise.all([
        this.loadHouseholdMembers(parentId),
        this.loadRooms(parentId),
        this.loadChores(parentId),
        this.loadPendingCompletions(parentId)
      ]);

      // Establish SSE connection for real-time updates
      this.connectToEventStream(parentId);

      update(state => ({ ...state, loading: false, error: null }));
    } catch (error) {
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to initialize parent data'
      }));
    }
  }
};

// Derived stores for computed values
export const currentParent = derived(choresStore, ($store) => $store.currentParent);
export const isAuthenticated = derived(choresStore, ($store) => $store.isAuthenticated);
export const rooms = derived(choresStore, ($store) => $store.rooms);
export const chores = derived(choresStore, ($store) => $store.chores);
export const householdMembers = derived(choresStore, ($store) => $store.householdMembers);
export const currentMember = derived(choresStore, ($store) => $store.currentMember);
export const pendingCompletions = derived(choresStore, ($store) => $store.pendingCompletions);
export const weeklyPoints = derived(choresStore, ($store) => $store.weeklyPoints);
export const allowanceCalculations = derived(choresStore, ($store) => $store.allowanceCalculations);
export const loading = derived(choresStore, ($store) => $store.loading);
export const error = derived(choresStore, ($store) => $store.error);
export const selectedRoomId = derived(choresStore, ($store) => $store.selectedRoomId);
export const dashboard = derived(choresStore, ($store) => $store.dashboard);
export const isConnected = derived(choresStore, ($store) => $store.isConnected);

// Derived stores for filtered data
export const choresByRoom = derived(
  [chores, selectedRoomId],
  ([$chores, $selectedRoomId]) => {
    if (!$selectedRoomId) return $chores;
    return $chores.filter(chore => chore.room_id === $selectedRoomId);
  }
);

export const availableChores = derived(chores, ($chores) => 
  $chores.filter(chore => chore.is_active && (!chore.next_available_at || new Date(chore.next_available_at) <= new Date()))
);

export const disabledChores = derived(chores, ($chores) => 
  $chores.filter(chore => chore.is_active && chore.next_available_at && new Date(chore.next_available_at) > new Date())
);

export const pendingChores = derived(chores, ($chores) => 
  $chores.filter(chore => chore.status === 'pending')
);

export const completedChores = derived(chores, ($chores) => 
  $chores.filter(chore => chore.status === 'completed')
);

// Weekly points summary
export const weeklyPointsSummary = derived(weeklyPoints, ($weeklyPoints) => {
  const currentWeek = $weeklyPoints[0]; // Assuming first item is current week
  if (!currentWeek) {
    return {
      current_week_points: 0,
      max_weekly_points: 30,
      points_remaining: 30,
      is_at_cap: false
    };
  }
  
  return {
    current_week_points: currentWeek.points_capped,
    max_weekly_points: 30,
    points_remaining: Math.max(0, 30 - currentWeek.points_capped),
    is_at_cap: currentWeek.points_capped >= 30
  };
});

// Allowance summary for current member
export const currentMemberAllowance = derived(
  [allowanceCalculations, currentMember],
  ([$calculations, $currentMember]) => {
    if (!$currentMember) return null;
    
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM format
    const calculation = $calculations.find(c => 
      c.member_id === $currentMember.id && c.month_year === currentMonth
    );
    
    if (!calculation) return null;
    
    return {
      current_month_allowance: calculation.allowance_amount,
      total_points_earned: calculation.total_points_earned,
      total_points_possible: calculation.total_points_possible,
      completion_percentage: calculation.completion_percentage,
      age_category: calculation.age_category,
      rate_per_point: calculation.age_category === 'teenager' ? $currentMember.age : 0.50
    };
  }
);

// Frequency labels and colors
export const frequencyLabels = {
  daily: 'Daily',
  weekly: 'Weekly',
  monthly: 'Monthly'
} as const;

export const frequencyColors = {
  daily: 'text-blue-600 bg-blue-100',
  weekly: 'text-green-600 bg-green-100',
  monthly: 'text-purple-600 bg-purple-100'
} as const;

// Age category colors
export const ageCategoryColors = {
  child: 'text-pink-600 bg-pink-100',
  preteen: 'text-orange-600 bg-orange-100',
  teenager: 'text-blue-600 bg-blue-100',
  adult: 'text-gray-600 bg-gray-100'
} as const;

// Status colors
export const statusColors = {
  pending: 'text-yellow-600 bg-yellow-100',
  completed: 'text-green-600 bg-green-100',
  disabled: 'text-gray-600 bg-gray-100'
} as const;
