<!--
  Grocery Item Card Component
  
  Displays a single grocery item with edit, delete, and toggle functionality.
  Supports inline editing and priority-based styling.
-->

<script lang="ts">
  import type { GroceryItem } from '$lib/stores/grocery';
  import { priorityColors, priorityLabels } from '$lib/stores/grocery';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    edit: GroceryItem;
    update: Partial<GroceryItem>;
    delete: void;
    toggle: void;
  }>();

  // Props
  export let item: GroceryItem;
  export let editingItem: GroceryItem | null = null;

  // Local state
  let isEditing = false;
  let editName = '';
  let editQuantity = '';
  let editCategory = '';
  let editNotes = '';
  let editPriority: 'low' | 'medium' | 'high' = 'medium';

  // Common categories for quick selection
  const commonCategories = [
    'Produce',
    'Dairy',
    'Meat',
    'Pantry',
    'Frozen',
    'Beverages',
    'Snacks',
    'Household',
    'Personal Care'
  ];

  // Watch for editing state changes
  $: if (editingItem?.id === item.id) {
    isEditing = true;
    editName = item.name;
    editQuantity = item.quantity || '';
    editCategory = item.category || '';
    editNotes = item.notes || '';
    editPriority = item.priority;
  } else {
    isEditing = false;
  }

  // Handle edit button click
  function handleEdit() {
    dispatch('edit', item);
  }

  // Handle save changes
  function handleSave() {
    const updates: Partial<GroceryItem> = {
      name: editName.trim(),
      quantity: editQuantity.trim() || undefined,
      category: editCategory.trim() || undefined,
      notes: editNotes.trim() || undefined,
      priority: editPriority
    };

    dispatch('update', updates);
  }

  // Handle cancel edit
  function handleCancel() {
    isEditing = false;
  }

  // Handle delete
  function handleDelete() {
    dispatch('delete');
  }

  // Handle toggle completion
  function handleToggle() {
    dispatch('toggle');
  }

  // Get priority badge class
  function getPriorityClass(priority: string) {
    return priorityColors[priority as keyof typeof priorityColors] || priorityColors.medium;
  }

  // Format date for display
  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }
</script>

<div class="grocery-item-card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow {item.completed ? 'opacity-75' : ''}">
  {#if isEditing}
    <!-- Edit Mode -->
    <div class="space-y-3">
      <!-- Item Name -->
      <div>
        <input
          type="text"
          bind:value={editName}
          placeholder="Item name"
          class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          maxlength="100"
        />
      </div>

      <!-- Quantity and Category -->
      <div class="grid grid-cols-2 gap-2">
        <input
          type="text"
          bind:value={editQuantity}
          placeholder="Quantity"
          class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          maxlength="50"
        />
        <select
          bind:value={editCategory}
          class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="">Category</option>
          {#each commonCategories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
      </div>

      <!-- Priority -->
      <div class="flex gap-1">
        {#each Object.entries(priorityLabels) as [key, label]}
          <label class="flex items-center">
            <input
              type="radio"
              bind:group={editPriority}
              value={key}
              class="sr-only"
            />
            <span class="px-2 py-1 text-xs font-medium rounded cursor-pointer transition-colors {
              editPriority === key
                ? 'bg-blue-100 text-blue-800 border border-blue-300'
                : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
            }">
              {label}
            </span>
          </label>
        {/each}
      </div>

      <!-- Notes -->
      <textarea
        bind:value={editNotes}
        placeholder="Notes"
        rows="2"
        class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        maxlength="200"
      ></textarea>

      <!-- Edit Actions -->
      <div class="flex justify-end gap-2">
        <button
          on:click={handleCancel}
          class="px-2 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
        >
          Cancel
        </button>
        <button
          on:click={handleSave}
          class="px-2 py-1 text-xs text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors"
        >
          Save
        </button>
      </div>
    </div>
  {:else}
    <!-- Display Mode -->
    <div class="flex items-start gap-3">
      <!-- Checkbox -->
      <button
        on:click={handleToggle}
        class="flex-shrink-0 mt-0.5 w-4 h-4 border-2 border-gray-300 dark:border-gray-600 rounded {item.completed ? 'bg-green-500 border-green-500' : 'hover:border-gray-400'} transition-colors"
        aria-label={item.completed ? 'Mark as pending' : 'Mark as completed'}
      >
        {#if item.completed}
          <svg class="w-full h-full text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        {/if}
      </button>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <!-- Header -->
        <div class="flex items-start justify-between gap-2 mb-1">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white {item.completed ? 'line-through' : ''}">
            {item.name}
          </h4>
          <div class="flex items-center gap-1">
            <!-- Priority Badge -->
            <span class="px-2 py-0.5 text-xs font-medium rounded-full {getPriorityClass(item.priority)}">
              {priorityLabels[item.priority]}
            </span>
          </div>
        </div>

        <!-- Details -->
        <div class="space-y-1">
          {#if item.quantity || item.category}
            <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
              {#if item.quantity}
                <span class="font-medium">{item.quantity}</span>
              {/if}
              {#if item.category}
                <span class="text-gray-400">•</span>
                <span>{item.category}</span>
              {/if}
            </div>
          {/if}

          {#if item.notes}
            <p class="text-xs text-gray-600 dark:text-gray-400 italic">
              {item.notes}
            </p>
          {/if}

          <div class="text-xs text-gray-500 dark:text-gray-500">
            Added {formatDate(item.created_at)}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-1">
        <button
          on:click={handleEdit}
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          aria-label="Edit item"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          on:click={handleDelete}
          class="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
          aria-label="Delete item"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  {/if}
</div> 