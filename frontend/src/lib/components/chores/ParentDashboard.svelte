<!--
  Parent Dashboard Component
  
  Comprehensive dashboard for parents to manage the chore system.
  Includes member management, room management, chore management, and pending approvals.
-->

<script lang="ts">
  import { chores, choresStore, error, householdMembers, loading, pendingCompletions, rooms, type Chore, type ChoreCompletion, type HouseholdMember, type Room } from '$lib/stores/chores.js';
  import { onMount } from 'svelte';
  import ChoreManagement from './ChoreManagement.svelte';
  import MemberManagement from './MemberManagement.svelte';
  import PendingApprovals from './PendingApprovals.svelte';
  import RoomManagement from './RoomManagement.svelte';

  // Props
  export let onClose: () => void;

  // State
  let activeTab: 'members' | 'rooms' | 'chores' | 'approvals' = 'approvals';
  let members: HouseholdMember[] = [];
  let roomList: Room[] = [];
  let choreList: Chore[] = [];
  let pendingList: ChoreCompletion[] = [];
  let isLoading = false;
  let errorMessage = '';

  // Reactive statements
  $: members = $householdMembers;
  $: roomList = $rooms;
  $: choreList = $chores;
  $: pendingList = $pendingCompletions;
  $: isLoading = $loading;
  $: errorMessage = $error;

  onMount(() => {
    // Load all parent data
    const parent = $choresStore.currentParent;
    if (parent) {
      choresStore.initializeParentData(parent.id);
    }
  });

  function switchTab(tab: 'members' | 'rooms' | 'chores' | 'approvals') {
    activeTab = tab;
  }

  function handleMemberCreated(member: HouseholdMember) {
    // Member will be added to the store automatically
  }

  function handleMemberUpdated(member: HouseholdMember) {
    // Member will be updated in the store automatically
  }

  function handleRoomCreated(room: Room) {
    // Room will be added to the store automatically
  }

  function handleRoomUpdated(room: Room) {
    // Room will be updated in the store automatically
  }

  function handleChoreCreated(chore: Chore) {
    // Chore will be added to the store automatically
  }

  function handleChoreUpdated(chore: Chore) {
    // Chore will be updated in the store automatically
  }

  function handleCompletionApproved(completionId: number) {
    const parent = $choresStore.currentParent;
    if (parent) {
      choresStore.confirmChoreCompletion(completionId, parent.id);
    }
  }

  function getTabClass(tab: string): string {
    const baseClass = "px-4 py-2 text-sm font-medium rounded-lg transition-colors";
    const activeClass = "bg-blue-100 text-blue-700";
    const inactiveClass = "text-gray-600 hover:text-gray-800 hover:bg-gray-100";
    
    return `${baseClass} ${activeTab === tab ? activeClass : inactiveClass}`;
  }

  function getPendingCount(): number {
    return pendingList.length;
  }
</script>

<div class="parent-dashboard h-full flex flex-col">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
    <div>
      <h2 class="text-2xl font-bold text-gray-900">Parent Dashboard</h2>
      <p class="text-sm text-gray-600">Manage your family's chore system</p>
    </div>
    <button
      on:click={onClose}
      class="text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Close"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <!-- Navigation Tabs -->
  <div class="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
    <button
      on:click={() => switchTab('approvals')}
      class={getTabClass('approvals')}
    >
      Pending Approvals
      {#if getPendingCount() > 0}
        <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          {getPendingCount()}
        </span>
      {/if}
    </button>
    
    <button
      on:click={() => switchTab('members')}
      class={getTabClass('members')}
    >
      Family Members
    </button>
    
    <button
      on:click={() => switchTab('rooms')}
      class={getTabClass('rooms')}
    >
      Rooms
    </button>
    
    <button
      on:click={() => switchTab('chores')}
      class={getTabClass('chores')}
    >
      Chores
    </button>
  </div>

  <!-- Content Area -->
  <div class="flex-1 min-h-0">
    {#if isLoading}
      <!-- Loading State -->
      <div class="flex items-center justify-center h-64">
        <div class="flex items-center space-x-2">
          <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-gray-600">Loading...</span>
        </div>
      </div>
    {:else if errorMessage}
      <!-- Error State -->
      <div class="flex items-center justify-center h-64">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
          <p class="text-gray-600 mb-4">{errorMessage}</p>
          <button
            on:click={() => window.location.reload()}
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    {:else}
      <!-- Tab Content -->
      {#if activeTab === 'approvals'}
        <PendingApprovals
          completions={pendingList}
          onApproved={handleCompletionApproved}
        />
      {:else if activeTab === 'members'}
        <MemberManagement
          members={members}
          onMemberCreated={handleMemberCreated}
          onMemberUpdated={handleMemberUpdated}
        />
      {:else if activeTab === 'rooms'}
        <RoomManagement
          rooms={roomList}
          onRoomCreated={handleRoomCreated}
          onRoomUpdated={handleRoomUpdated}
        />
      {:else if activeTab === 'chores'}
        <ChoreManagement
          chores={choreList}
          rooms={roomList}
          onChoreCreated={handleChoreCreated}
          onChoreUpdated={handleChoreUpdated}
        />
      {/if}
    {/if}
  </div>
</div>

<style>
  .parent-dashboard {
    min-height: 0;
  }
</style>
