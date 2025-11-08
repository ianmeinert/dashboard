<!--
  Chores List Component
  
  Displays a list of chores with filtering and actions.
-->

<script lang="ts">
  import { chores } from '$lib/stores/chores';
  import AddChoreModal from './AddChoreModal.svelte';
  import ChoreCard from './ChoreCard.svelte';

  let showAddModal = false;
  let filterStatus: 'all' | 'completed' | 'upcoming' | 'past_due' | 'open_to_work' = 'all';


  // Get today's date for comparison
  $: today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

  // Filter chores based on selected filters
  $: filteredChores = $chores.filter(chore => {
    
    // Then apply status filter
    if (filterStatus === 'all') return true;
    
    if (filterStatus === 'completed') {
      return chore.status === 'completed';
    }
    
    if (filterStatus === 'upcoming') {
      // Chores due in the future (not yet available to work)
      return chore.due_date && chore.due_date > today && chore.status === 'pending';
    }
    
    if (filterStatus === 'past_due') {
      // Chores that are overdue
      return chore.status === 'overdue';
    }
    
    if (filterStatus === 'open_to_work') {
      // Chores that can be worked on today (due today or in the past, but not completed and not overdue)
      if (chore.status === 'completed') return false;
      if (chore.status === 'overdue') return false; // Exclude overdue chores from open_to_work
      if (!chore.due_date) return true; // No due date means always available
      return chore.due_date <= today; // Due today or in the past
    }
    
    return true;
  });

  // Group chores by logical categories for better organization
  $: groupedChores = {
    open_to_work: filteredChores.filter(c => {
      if (c.status === 'completed') return false;
      if (c.status === 'overdue') return false; // Exclude overdue from open_to_work group
      if (!c.due_date) return true;
      return c.due_date <= today;
    }),
    past_due: filteredChores.filter(c => c.status === 'overdue'),
    upcoming: filteredChores.filter(c => {
      return c.due_date && c.due_date > today && c.status === 'pending';
    }),
    completed: filteredChores.filter(c => c.status === 'completed'),
  };

  function handleAddChore() {
    showAddModal = true;
  }

  function handleChoreAdded() {
    showAddModal = false;
  }
</script>

<div class="chores-list">
  <!-- Filters and Actions -->
  <div class="flex flex-wrap items-center justify-between gap-3 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
    <div class="flex items-center gap-3">
      <!-- Status Filter -->
      <div class="flex items-center gap-2">
        <label for="status-filter" class="text-sm font-medium text-gray-700 dark:text-gray-300">
          Status:
        </label>
        <select
          id="status-filter"
          bind:value={filterStatus}
          class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="all">All</option>
          <option value="open_to_work">Open to Work</option>
          <option value="upcoming">Upcoming</option>
          <option value="past_due">Past Due</option>
          <option value="completed">Completed</option>
        </select>
      </div>      
    </div>

    <!-- Add Chore Button -->
    <button
      on:click={handleAddChore}
      class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
    >
      + Add Chore
    </button>
  </div>

  <!-- Chores Display -->
  {#if filteredChores.length === 0}
    <div class="text-center py-8 text-gray-500">
      <p class="text-lg font-medium mb-2">No chores found</p>
      <p class="text-sm">Try adjusting your filters or add a new chore!</p>
    </div>
  {:else}
    <div class="space-y-6">
      <!-- Show only the selected filter category, or all if 'all' is selected -->
      
      <!-- Past Due Chores -->
      {#if (filterStatus === 'all' || filterStatus === 'past_due') && groupedChores.past_due.length > 0}
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 bg-red-500 rounded-full"></span>
            <h4 class="text-md font-medium text-red-700 dark:text-red-400">
              Past Due ({groupedChores.past_due.length})
            </h4>
          </div>
          <div class="space-y-2">
            {#each groupedChores.past_due as chore (chore.id)}
              <ChoreCard {chore} />
            {/each}
          </div>
        </div>
      {/if}

      <!-- Open to Work -->
      {#if (filterStatus === 'all' || filterStatus === 'open_to_work') && groupedChores.open_to_work.length > 0}
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
            <h4 class="text-md font-medium text-green-700 dark:text-green-400">
              Open to Work ({groupedChores.open_to_work.length})
            </h4>
          </div>
          <div class="space-y-2">
            {#each groupedChores.open_to_work as chore (chore.id)}
              <ChoreCard {chore} />
            {/each}
          </div>
        </div>
      {/if}

      <!-- Upcoming Chores -->
      {#if (filterStatus === 'all' || filterStatus === 'upcoming') && groupedChores.upcoming.length > 0}
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
            <h4 class="text-md font-medium text-blue-700 dark:text-blue-400">
              Upcoming ({groupedChores.upcoming.length})
            </h4>
          </div>
          <div class="space-y-2">
            {#each groupedChores.upcoming as chore (chore.id)}
              <ChoreCard {chore} />
            {/each}
          </div>
        </div>
      {/if}

      <!-- Completed Chores -->
      {#if (filterStatus === 'all' || filterStatus === 'completed') && groupedChores.completed.length > 0}
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
            <h4 class="text-md font-medium text-green-700 dark:text-green-400">
              Completed ({groupedChores.completed.length})
            </h4>
          </div>
          <div class="space-y-2 opacity-75">
            {#each groupedChores.completed as chore (chore.id)}
              <ChoreCard {chore} />
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Add Chore Modal -->
{#if showAddModal}
  <AddChoreModal
    on:close={() => showAddModal = false}
    on:added={handleChoreAdded}
  />
{/if}
