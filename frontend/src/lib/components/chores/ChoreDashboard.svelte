<!--
  Chore Dashboard Component
  
  Main dashboard for viewing and completing chores.
  Shows rooms, chores, and progress tracking.
-->

<script lang="ts">
  import { availableChores, chores, choresStore, currentMemberAllowance, error, loading, rooms, selectedRoomId, weeklyPointsSummary, type Chore, type Room } from '$lib/stores/chores.js';
  import { onMount } from 'svelte';
  import ChoreList from './ChoreList.svelte';
  import ProgressSummary from './ProgressSummary.svelte';
  import RoomSelector from './RoomSelector.svelte';

  // Props
  export let compact: boolean = false;

  // State
  let roomList: Room[] = [];
  let choreList: Chore[] = [];
  let selectedRoom: number | null = null;
  let isLoading = false;
  let errorMessage = '';
  let weeklySummary: any = null;
  let allowanceSummary: any = null;

  // Reactive statements
  $: roomList = $rooms;
  $: choreList = $chores;
  $: selectedRoom = $selectedRoomId;
  $: isLoading = $loading;
  $: errorMessage = $error;
  $: weeklySummary = $weeklyPointsSummary;
  $: allowanceSummary = $currentMemberAllowance;

  onMount(() => {
    // Load dashboard data
    const parent = $choresStore.currentParent;
    const member = $choresStore.currentMember;
    
    if (parent && member) {
      choresStore.loadDashboard(parent.id, member.id);
    }
  });

  function handleRoomSelected(roomId: number | null) {
    choresStore.setSelectedRoom(roomId);
  }

  function handleChoreCompleted(choreId: number) {
    const member = $choresStore.currentMember;
    if (member) {
      choresStore.completeChore(choreId, member.id);
    }
  }

  function getRoomColor(room: Room): string {
    return room.color_code || '#6B7280';
  }

  function getRoomChores(roomId: number): Chore[] {
    return choreList.filter(chore => chore.room_id === roomId);
  }

  function getTotalChores(): number {
    return choreList.length;
  }

  function getAvailableChores(): number {
    return availableChores.length;
  }

  function getCompletedChores(): number {
    return choreList.filter(chore => chore.status === 'completed').length;
  }

  function getPendingChores(): number {
    return choreList.filter(chore => chore.status === 'pending').length;
  }
</script>

<div class="chore-dashboard h-full flex flex-col">
  {#if isLoading}
    <!-- Loading State -->
    <div class="flex-1 flex items-center justify-center">
      <div class="flex items-center space-x-2">
        <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600">Loading chores...</span>
      </div>
    </div>
  {:else if errorMessage}
    <!-- Error State -->
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Chores</h3>
        <p class="text-gray-600 mb-4">{errorMessage}</p>
        <button
          on:click={() => window.location.reload()}
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  {:else if roomList.length === 0}
    <!-- No Rooms State -->
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Rooms Available</h3>
        <p class="text-gray-600 mb-4">No rooms have been set up for chores yet.</p>
        <p class="text-sm text-gray-500">Use the Parent Dashboard to add rooms and chores.</p>
      </div>
    </div>
  {:else}
    <!-- Main Dashboard -->
    <div class="flex-1 flex flex-col space-y-4">
      <!-- Progress Summary -->
      {#if !compact}
        <ProgressSummary 
          {weeklySummary}
          {allowanceSummary}
          totalChores={getTotalChores()}
          availableChores={getAvailableChores()}
          completedChores={getCompletedChores()}
          pendingChores={getPendingChores()}
        />
      {/if}

      <!-- Room Selector -->
      <RoomSelector
        rooms={roomList}
        selectedRoom={selectedRoom}
        onRoomSelected={handleRoomSelected}
        {compact}
      />

      <!-- Chore List -->
      <div class="flex-1 min-h-0">
        <ChoreList
          chores={selectedRoom ? getRoomChores(selectedRoom) : choreList}
          onChoreCompleted={handleChoreCompleted}
          {compact}
        />
      </div>
    </div>
  {/if}
</div>

<style>
  .chore-dashboard {
    min-height: 0;
  }
</style>
