<!--
  Add Item Form Component
  
  A form for adding new grocery items with validation and priority selection.
-->

<script lang="ts">
  import type { GroceryItemCreate } from '$lib/stores/grocery';
  import { priorityLabels } from '$lib/stores/grocery';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    add: GroceryItemCreate;
  }>();

  // Form state
  let name = '';
  let quantity = '';
  let category = '';
  let notes = '';
  let priority: 'low' | 'medium' | 'high' = 'medium';
  let errors: Record<string, string> = {};

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

  // Validate form
  function validateForm(): boolean {
    errors = {};
    
    if (!name.trim()) {
      errors.name = 'Item name is required';
    } else if (name.length > 100) {
      errors.name = 'Item name must be 100 characters or less';
    }

    if (quantity && quantity.length > 50) {
      errors.quantity = 'Quantity must be 50 characters or less';
    }

    if (category && category.length > 50) {
      errors.category = 'Category must be 50 characters or less';
    }

    if (notes && notes.length > 200) {
      errors.notes = 'Notes must be 200 characters or less';
    }

    return Object.keys(errors).length === 0;
  }

  // Handle form submission
  function handleSubmit() {
    if (!validateForm()) {
      return;
    }

    const newItem: GroceryItemCreate = {
      name: name.trim(),
      quantity: quantity.trim() || undefined,
      category: category.trim() || undefined,
      notes: notes.trim() || undefined,
      priority
    };

    dispatch('add', newItem);
  }

  // Reset form
  function resetForm() {
    name = '';
    quantity = '';
    category = '';
    notes = '';
    priority = 'medium';
    errors = {};
  }

  // Handle key press for quick submission
  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4">
  <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
    <!-- Item Name -->
    <div class="mb-3">
      <label for="item-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Item Name *
      </label>
      <input
        id="item-name"
        type="text"
        bind:value={name}
        on:input={() => { if (errors.name) errors.name = ''; }}
        on:keypress={handleKeyPress}
        placeholder="e.g., Bananas, Milk, Bread"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white {errors.name ? 'border-red-500' : ''}"
        maxlength="100"
      />
      {#if errors.name}
        <p class="mt-1 text-sm text-red-600">{errors.name}</p>
      {/if}
    </div>

    <!-- Quantity and Category Row -->
    <div class="grid grid-cols-2 gap-3 mb-3">
      <!-- Quantity -->
      <div>
        <label for="item-quantity" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Quantity
        </label>
        <input
          id="item-quantity"
          type="text"
          bind:value={quantity}
          placeholder="e.g., 2 lbs, 1 dozen"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white {errors.quantity ? 'border-red-500' : ''}"
          maxlength="50"
        />
        {#if errors.quantity}
          <p class="mt-1 text-sm text-red-600">{errors.quantity}</p>
        {/if}
      </div>

      <!-- Category -->
      <div>
        <label for="item-category" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Category
        </label>
        <select
          id="item-category"
          bind:value={category}
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white {errors.category ? 'border-red-500' : ''}"
        >
          <option value="">Select category</option>
          {#each commonCategories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
        {#if errors.category}
          <p class="mt-1 text-sm text-red-600">{errors.category}</p>
        {/if}
      </div>
    </div>

    <!-- Priority -->
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Priority
      </label>
      <div class="flex gap-2">
        {#each Object.entries(priorityLabels) as [key, label]}
          <label class="flex items-center">
            <input
              type="radio"
              bind:group={priority}
              value={key}
              class="sr-only"
            />
            <span class="px-3 py-1.5 text-sm font-medium rounded-md cursor-pointer transition-colors {
              priority === key
                ? 'bg-blue-100 text-blue-800 border border-blue-300'
                : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
            }">
              {label}
            </span>
          </label>
        {/each}
      </div>
    </div>

    <!-- Notes -->
    <div class="mb-4">
      <label for="item-notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Notes
      </label>
      <textarea
        id="item-notes"
        bind:value={notes}
        placeholder="Any additional notes..."
        rows="2"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white {errors.notes ? 'border-red-500' : ''}"
        maxlength="200"
      ></textarea>
      {#if errors.notes}
        <p class="mt-1 text-sm text-red-600">{errors.notes}</p>
      {/if}
    </div>

    <!-- Submit Button -->
    <div class="flex justify-end gap-2">
      <button
        type="button"
        on:click={resetForm}
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:hover:bg-gray-600"
      >
        Reset
      </button>
      <button
        type="submit"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        Add Item
      </button>
    </div>
  </div>
</form> 