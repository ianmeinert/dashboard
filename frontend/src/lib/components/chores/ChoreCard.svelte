<!--
  Chore Card Component
  
  Displays individual chore details with actions.
-->

<script lang="ts">
  import type { Chore } from '$lib/stores/chores';
  import { categoryColors, categoryLabels, choresStore, priorityColors, priorityLabels } from '$lib/stores/chores';
  import CompleteChoreModal from './CompleteChoreModal.svelte';

  export let chore: Chore;

  let showCompleteModal = false;
  let isEditing = false;

  function handleComplete() {
    showCompleteModal = true;
  }

  function handleEdit() {
    isEditing = true;
    // TODO: Open edit modal
  }

  async function handleDelete() {
    if (confirm(`Are you sure you want to delete "${chore.title}"?`)) {
      try {
        await choresStore.deleteChore(chore.id);
      } catch (error) {
        console.error('Failed to delete chore:', error);
      }
    }
  }

  function handleCompleted() {
    showCompleteModal = false;
  }

  // Format date for display
  function formatDate(dateString?: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // Check if chore should show overdue styling (use backend status)
  function isOverdue(): boolean {
    return chore.status === 'overdue';
  }

  $: dueDateDisplay = formatDate(chore.due_date);
  $: overdueStatus = isOverdue();
</script>

<div class="chore-card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-all {overdueStatus ? 'border-red-300 bg-red-50 dark:bg-red-900/10' : ''}">
  <div class="flex items-start justify-between gap-3">
    <!-- Left: Chore Info -->
    <div class="flex-1 min-w-0">
      <!-- Title and Status -->
      <div class="flex items-start gap-2 mb-2">
        <h5 class="font-semibold text-gray-900 dark:text-white {chore.status === 'completed' ? 'line-through text-gray-500' : ''}">
          {chore.title}
        </h5>
        {#if chore.status === 'completed'}
          <span class="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800 rounded">
            ✓ Done
          </span>
        {:else if overdueStatus}
          <span class="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800 rounded">
            Overdue
          </span>
        {/if}
      </div>

      <!-- Description -->
      {#if chore.description}
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
          {chore.description}
        </p>
      {/if}

      <!-- Metadata Tags -->
      <div class="flex flex-wrap items-center gap-2 mb-2">
        <!-- Category -->
        <span class="px-2 py-1 text-xs font-medium rounded-full {categoryColors[chore.category]}">
          {categoryLabels[chore.category]}
        </span>

        <!-- Priority -->
        <span class="px-2 py-1 text-xs font-medium rounded-full {priorityColors[chore.priority]}">
          {priorityLabels[chore.priority]}
        </span>

        <!-- Points -->
        <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
          {chore.points} {chore.points === 1 ? 'pt' : 'pts'}
        </span>

        <!-- Due Date -->
        {#if chore.due_date}
          <span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full {overdueStatus ? 'bg-red-100 text-red-700' : ''}">
            📅 {dueDateDisplay}
          </span>
        {/if}

        <!-- Time Estimate -->
        {#if chore.estimated_minutes}
          <span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
            ⏱️ {chore.estimated_minutes}m
          </span>
        {/if}

        <!-- Recurring -->
        {#if chore.recurrence_type && chore.recurrence_type !== 'none'}
          <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
            🔁 {chore.recurrence_type}
          </span>
        {/if}
      </div>      
    </div>

    <!-- Right: Actions -->
    <div class="flex flex-col gap-2">
      {#if chore.status !== 'completed'}
        <button
          on:click={handleComplete}
          class="px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 rounded transition-colors"
          title="Mark as complete"
        >
          ✓ Complete
        </button>
      {/if}

      <button
        on:click={handleEdit}
        class="px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors"
        title="Edit chore"
      >
        ✏️ Edit
      </button>

      <button
        on:click={handleDelete}
        class="px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition-colors"
        title="Delete chore"
      >
        🗑️ Delete
      </button>
    </div>
  </div>

  <!-- Notes (if any) -->
  {#if chore.notes}
    <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
      <p class="text-xs text-gray-600 dark:text-gray-400">
        <span class="font-medium">Notes:</span> {chore.notes}
      </p>
    </div>
  {/if}
</div>

<!-- Complete Chore Modal -->
{#if showCompleteModal}
  <CompleteChoreModal
    {chore}
    on:close={() => showCompleteModal = false}
    on:completed={handleCompleted}
  />
{/if}

<style>
  .chore-card {
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .chore-card:hover {
    transform: translateY(-1px);
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
