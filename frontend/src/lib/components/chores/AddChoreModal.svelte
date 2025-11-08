<!--
  Add Chore Modal
  
  Modal for creating a new chore with all necessary fields.
-->

<script lang="ts">
  import type { ChoreCategory, ChoreCreate, ChorePriority, RecurrencePattern } from '$lib/stores/chores';
  import { choresStore, members } from '$lib/stores/chores';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  // Form fields
  let title = '';
  let description = '';
  let points = 1;
  let category: ChoreCategory = 'other';
  let priority: ChorePriority = 'medium';
  let assignedToId: number | undefined = undefined;
  let createdById: number = 1; // Default to first member, should be set by parent
  let dueDate = '';
  let recurrenceType: RecurrencePattern = 'none';
  let recurrenceInterval = 1;
  let notes = '';
  let estimatedMinutes: number | undefined = undefined;

  let submitting = false;
  let error = '';

  // Get default creator (first member)
  $: if ($members.length > 0 && !createdById) {
    createdById = $members[0].id;
  }

  const categories: { value: ChoreCategory; label: string }[] = [
    { value: 'cleaning', label: 'Cleaning' },
    { value: 'cooking', label: 'Cooking' },
    { value: 'dishes', label: 'Dishes' },
    { value: 'laundry', label: 'Laundry' },
    { value: 'trash', label: 'Trash' },
    { value: 'pets', label: 'Pets' },
    { value: 'yard', label: 'Yard Work' },
    { value: 'maintenance', label: 'Maintenance' },
    { value: 'organizing', label: 'Organizing' },
    { value: 'other', label: 'Other' },
  ];

  const priorities: { value: ChorePriority; label: string }[] = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
  ];

  const recurrenceTypes: { value: RecurrencePattern; label: string }[] = [
    { value: 'none', label: 'One-time' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'biweekly', label: 'Bi-weekly' },
    { value: 'monthly', label: 'Monthly' },
  ];

  // Helper function to get proper recurrence text
  function getRecurrenceText(type: RecurrencePattern, interval: number): string {
    if (type === 'none') return '';
    
    const singular = {
      'daily': 'day',
      'weekly': 'week',
      'biweekly': '2 weeks',
      'monthly': 'month'
    };
    
    const plural = {
      'daily': 'days',
      'weekly': 'weeks',
      'biweekly': `${interval * 2} weeks`,
      'monthly': 'months'
    };
    
    return interval === 1 ? singular[type] || type : plural[type] || type;
  }

  async function handleSubmit() {
    if (!title.trim()) {
      error = 'Title is required';
      return;
    }

    if (!createdById) {
      error = 'Creator is required';
      return;
    }

    submitting = true;
    error = '';

    const chore: ChoreCreate = {
      title: title.trim(),
      description: description.trim() || undefined,
      points,
      category,
      priority,
      assigned_to_id: assignedToId,
      created_by_id: createdById,
      due_date: dueDate || undefined,
      recurrence_type: recurrenceType !== 'none' ? recurrenceType : undefined,
      recurrence_interval: recurrenceType !== 'none' ? recurrenceInterval : undefined,
      notes: notes.trim() || undefined,
      estimated_minutes: estimatedMinutes,
    };

    try {
      await choresStore.createChore(chore);
      dispatch('added');
      dispatch('close');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create chore';
      submitting = false;
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
  class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
  on:click={handleBackdropClick}
  on:keydown={(e) => e.key === 'Escape' && handleCancel()}
  role="button"
  tabindex="0"
>
  <!-- Modal Content -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full p-6 my-8" on:click|stopPropagation>
    <!-- Header -->
    <div class="flex items-start justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Add New Chore</h3>
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
      <!-- Title -->
      <div>
        <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Title <span class="text-red-500">*</span>
        </label>
        <input
          id="title"
          type="text"
          bind:value={title}
          required
          maxlength="200"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="e.g., Wash the dishes"
        />
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Description
        </label>
        <textarea
          id="description"
          bind:value={description}
          rows="2"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"
          placeholder="Additional details about this chore..."
        ></textarea>
      </div>

      <!-- Row 1: Category, Priority, Points -->
      <div class="grid grid-cols-3 gap-4">
        <!-- Category -->
        <div>
          <label for="category" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Category
          </label>
          <select
            id="category"
            bind:value={category}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            {#each categories as cat}
              <option value={cat.value}>{cat.label}</option>
            {/each}
          </select>
        </div>

        <!-- Priority -->
        <div>
          <label for="priority" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Priority
          </label>
          <select
            id="priority"
            bind:value={priority}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            {#each priorities as pri}
              <option value={pri.value}>{pri.label}</option>
            {/each}
          </select>
        </div>

        <!-- Points -->
        <div>
          <label for="points" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Points
          </label>
          <input
            id="points"
            type="number"
            bind:value={points}
            min="1"
            max="10"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
      </div>

      <!-- Row 3: Due Date, Time Estimate -->
      <div class="grid grid-cols-2 gap-4">
        <!-- Due Date -->
        <div>
          <label for="due-date" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Due Date
          </label>
          <input
            id="due-date"
            type="date"
            bind:value={dueDate}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        <!-- Estimated Minutes -->
        <div>
          <label for="estimated-minutes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Time Estimate (min)
          </label>
          <input
            id="estimated-minutes"
            type="number"
            bind:value={estimatedMinutes}
            min="1"
            max="1440"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Optional"
          />
        </div>
      </div>

      <!-- Recurrence Section -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg space-y-3">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Recurrence</h4>
        
        <div class="grid grid-cols-2 gap-4">
          <!-- Recurrence Type -->
          <div>
            <label for="recurrence-type" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Pattern
            </label>
            <select
              id="recurrence-type"
              bind:value={recurrenceType}
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {#each recurrenceTypes as type}
                <option value={type.value}>{type.label}</option>
              {/each}
            </select>
          </div>

          <!-- Recurrence Interval -->
          {#if recurrenceType !== 'none'}
            <div>
              <label for="recurrence-interval" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                Every
              </label>
              <input
                id="recurrence-interval"
                type="number"
                bind:value={recurrenceInterval}
                min="1"
                max="30"
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          {/if}
        </div>

        {#if recurrenceType !== 'none'}
          <p class="text-xs text-gray-500 dark:text-gray-400">
            This chore will repeat every {recurrenceInterval} {getRecurrenceText(recurrenceType, recurrenceInterval)}.
          </p>
        {/if}
      </div>

      <!-- Notes -->
      <div>
        <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Notes
        </label>
        <textarea
          id="notes"
          bind:value={notes}
          rows="2"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"
          placeholder="Any additional notes..."
        ></textarea>
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
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={submitting || !title.trim()}
        >
          {submitting ? 'Creating...' : 'Create Chore'}
        </button>
      </div>
    </form>
  </div>
</div>