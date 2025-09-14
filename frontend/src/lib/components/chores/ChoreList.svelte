<!--
  Chore List Component
  
  Displays a list of chores with completion functionality.
-->

<script lang="ts">
  import { type Chore } from '$lib/stores/chores.js';
  import ChoreCard from './ChoreCard.svelte';

  // Props
  export let chores: Chore[];
  export let onChoreCompleted: (choreId: number) => void;
  export let compact: boolean = false;

  function handleChoreCompleted(choreId: number) {
    onChoreCompleted(choreId);
  }

  function getChoreStatus(chore: Chore): 'available' | 'disabled' | 'pending' | 'completed' {
    if (chore.status === 'completed') return 'completed';
    if (chore.status === 'pending') return 'pending';
    if (chore.next_available_at && new Date(chore.next_available_at) > new Date()) {
      return 'disabled';
    }
    return 'available';
  }

  function sortChores(chores: Chore[]): Chore[] {
    return [...chores].sort((a, b) => {
      // Sort by status: available first, then disabled, then pending, then completed
      const statusOrder = { available: 0, disabled: 1, pending: 2, completed: 3 };
      const aStatus = getChoreStatus(a);
      const bStatus = getChoreStatus(b);
      
      if (statusOrder[aStatus] !== statusOrder[bStatus]) {
        return statusOrder[aStatus] - statusOrder[bStatus];
      }
      
      // Then sort by points (highest first)
      if (a.points !== b.points) {
        return b.points - a.points;
      }
      
      // Finally sort by name
      return a.name.localeCompare(b.name);
    });
  }

  $: sortedChores = sortChores(chores);
  $: availableChores = sortedChores.filter(chore => getChoreStatus(chore) === 'available');
  $: disabledChores = sortedChores.filter(chore => getChoreStatus(chore) === 'disabled');
  $: pendingChores = sortedChores.filter(chore => getChoreStatus(chore) === 'pending');
  $: completedChores = sortedChores.filter(chore => getChoreStatus(chore) === 'completed');
</script>

<div class="chore-list">
  {#if chores.length === 0}
    <!-- No Chores State -->
    <div class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Chores Available</h3>
      <p class="text-gray-600">
        {#if compact}
          No chores in this room
        {:else}
          No chores have been set up yet. Use the Parent Dashboard to add chores.
        {/if}
      </p>
    </div>
  {:else}
    <!-- Chores List -->
    <div class="space-y-3">
      <!-- Available Chores -->
      {#if availableChores.length > 0}
        {#if !compact}
          <div class="flex items-center space-x-2 mb-3">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <h4 class="text-sm font-medium text-gray-700">Available ({availableChores.length})</h4>
          </div>
        {/if}
        
        <div class="space-y-2">
          {#each availableChores as chore (chore.id)}
            <ChoreCard
              {chore}
              status="available"
              onCompleted={() => handleChoreCompleted(chore.id)}
              {compact}
            />
          {/each}
        </div>
      {/if}

      <!-- Pending Chores -->
      {#if pendingChores.length > 0}
        {#if !compact}
          <div class="flex items-center space-x-2 mb-3 mt-6">
            <div class="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <h4 class="text-sm font-medium text-gray-700">Pending Approval ({pendingChores.length})</h4>
          </div>
        {/if}
        
        <div class="space-y-2">
          {#each pendingChores as chore (chore.id)}
            <ChoreCard
              {chore}
              status="pending"
              {compact}
            />
          {/each}
        </div>
      {/if}

      <!-- Disabled Chores -->
      {#if disabledChores.length > 0}
        {#if !compact}
          <div class="flex items-center space-x-2 mb-3 mt-6">
            <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
            <h4 class="text-sm font-medium text-gray-700">Not Available ({disabledChores.length})</h4>
          </div>
        {/if}
        
        <div class="space-y-2">
          {#each disabledChores as chore (chore.id)}
            <ChoreCard
              {chore}
              status="disabled"
              {compact}
            />
          {/each}
        </div>
      {/if}

      <!-- Completed Chores (only show in compact mode if there are any) -->
      {#if compact && completedChores.length > 0}
        <div class="space-y-2">
          {#each completedChores.slice(0, 2) as chore (chore.id)}
            <ChoreCard
              {chore}
              status="completed"
              {compact}
            />
          {/each}
          {#if completedChores.length > 2}
            <div class="text-xs text-gray-500 text-center py-2">
              +{completedChores.length - 2} more completed
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Summary Stats (only in compact mode) -->
    {#if compact && chores.length > 0}
      <div class="mt-4 pt-3 border-t border-gray-200">
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>{availableChores.length} available</span>
          <span>{pendingChores.length} pending</span>
          <span>{completedChores.length} completed</span>
        </div>
      </div>
    {/if}
  {/if}
</div>
