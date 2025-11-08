<!--
  Complete Chore Modal
  
  Modal for marking a chore as complete with optional notes and time tracking.
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { choresStore, members } from '$lib/stores/chores';
  import type { Chore, ChoreCompletionCreate } from '$lib/stores/chores';

  export let chore: Chore;

  const dispatch = createEventDispatcher();

  let completedById: number = chore.assigned_to_id || 0;
  let completionNotes = '';
  let actualMinutes: number | undefined = chore.estimated_minutes;
  let submitting = false;
  let error = '';

  async function handleSubmit() {
    // Prevent duplicate submissions
    if (submitting) {
      return;
    }

    if (!completedById) {
      error = 'Please select who completed this chore';
      return;
    }

    submitting = true;
    error = '';

    const completion: ChoreCompletionCreate = {
      chore_id: chore.id,
      completed_by_id: completedById,
      completion_notes: completionNotes || undefined,
      actual_minutes: actualMinutes,
    };

    try {
      await choresStore.completeChore(completion);
      dispatch('completed');
      dispatch('close');
    } catch (err: any) {
      // Extract the actual error message from the API response
      let errorMessage = 'Failed to complete chore';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err && typeof err === 'object') {
        // Check for common error response formats
        if (err.detail) {
          errorMessage = err.detail;
        } else if (err.message) {
          errorMessage = err.message;
        }
      }
      
      error = errorMessage;
      submitting = false;
      
      // Don't let this error bubble up to the global store
      // Clear any global error that might have been set
      choresStore.clearError();
    }
  }

  function handleCancel() {
    dispatch('close');
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleCancel();
    }
  }
</script>

<!-- Modal Backdrop -->
<div 
  class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
  on:click={handleBackdropClick}
  on:keydown={(e) => e.key === 'Escape' && handleCancel()}
  role="button"
  tabindex="0"
>
  <!-- Modal Content -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6" on:click|stopPropagation>
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">Complete Chore</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{chore.title}</p>
      </div>
      <button
        on:click={handleCancel}
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
        aria-label="Close"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Form -->
    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
      <!-- Who completed it -->
      <div>
        <label for="completed-by" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Who completed this? <span class="text-red-500">*</span>
        </label>
        <select
          id="completed-by"
          bind:value={completedById}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value={0} disabled>Select a family member</option>
          {#each $members as member (member.id)}
            <option value={member.id}>
              {member.name} ({member.weekly_points}/{member.weekly_points_cap} pts this week)
            </option>
          {/each}
        </select>
      </div>

      <!-- Time taken -->
      {#if chore.estimated_minutes}
        <div>
          <label for="actual-minutes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Time Spent (minutes)
            <span class="text-xs text-gray-500">Estimated: {chore.estimated_minutes}m</span>
          </label>
          <input
            id="actual-minutes"
            type="number"
            bind:value={actualMinutes}
            min="1"
            max="1440"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="How long did it take?"
          />
        </div>
      {/if}

      <!-- Completion notes -->
      <div>
        <label for="completion-notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Notes (optional)
        </label>
        <textarea
          id="completion-notes"
          bind:value={completionNotes}
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"
          placeholder="Any notes about completing this chore?"
        ></textarea>
      </div>

      <!-- Points display -->
      <div class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
        <p class="text-sm font-medium text-green-800 dark:text-green-300">
          🎉 This chore is worth <span class="font-bold">{chore.points} point{chore.points === 1 ? '' : 's'}</span>!
        </p>
      </div>

      <!-- Error message -->
      {#if error}
        <div class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-700">{error}</p>
        </div>
      {/if}

      <!-- Actions -->
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          on:click={handleCancel}
          class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
          disabled={submitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={submitting || !completedById}
        >
          {submitting ? 'Completing...' : 'Mark Complete'}
        </button>
      </div>
    </form>
  </div>
</div>
