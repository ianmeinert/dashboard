<!--
  Grocery List Component
  
  A comprehensive grocery list manager with add, edit, delete, and toggle functionality.
  Features priority levels, categories, and completion tracking.
-->

<script lang="ts">
  import type { GroceryItem, GroceryItemCreate } from '$lib/stores/grocery';
  import { completedItems, groceryStore, pendingItems, priorityColors, priorityLabels } from '$lib/stores/grocery';
  import { onMount } from 'svelte';
  import AddItemForm from './grocery/AddItemForm.svelte';
  import GroceryItemCard from './grocery/GroceryItemCard.svelte';

  // Component state
  let showAddForm = false;
  let showCompleted = false;
  let editingItem: GroceryItem | null = null;
  let addFormKey = 0;

  // Load items on component mount
  onMount(() => {
    groceryStore.loadItems();
  });

  // Handle adding new item
  async function handleAddItem(e: CustomEvent<GroceryItemCreate>) {
    await groceryStore.addItem(e.detail);
    showAddForm = false;
    addFormKey += 1; // Remount the form to reset it
  }

  // Handle editing item
  function handleEditItem(item: GroceryItem) {
    editingItem = item;
  }

  // Handle updating item
  function handleUpdateItem(itemId: number, updates: Partial<GroceryItem>) {
    groceryStore.updateItem(itemId, updates);
    editingItem = null;
  }

  // Handle deleting item
  function handleDeleteItem(itemId: number) {
    if (confirm('Are you sure you want to delete this item?')) {
      groceryStore.deleteItem(itemId);
    }
  }

  // Handle toggling item completion
  function handleToggleItem(itemId: number) {
    groceryStore.toggleItem(itemId);
  }

  // Handle clearing completed items
  function handleClearCompleted() {
    if (confirm('Are you sure you want to remove all completed items?')) {
      groceryStore.clearCompleted();
    }
  }

  // Get priority badge class
  function getPriorityClass(priority: string) {
    return priorityColors[priority as keyof typeof priorityColors] || priorityColors.medium;
  }

  export let compact: boolean = false;
  export let onShowAdd: (() => void) | undefined;
</script>

<div class="grocery-list h-full flex flex-col">
  {#if compact}
    <!-- Compact List View -->
    <ul class="divide-y divide-gray-200 dark:divide-gray-700">
      {#if $groceryStore.items.length === 0}
        <li class="py-4 text-center text-gray-500 flex flex-col items-center">
          <span>No grocery items yet</span>
          {#if typeof onShowAdd === 'function'}
            <button
              class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
              on:click={onShowAdd}
            >
              Add Item
            </button>
          {/if}
        </li>
      {:else}
        {#each $groceryStore.items as item (item.id)}
          <li class="flex items-center gap-3 py-2">
            <input type="checkbox" checked={item.completed} on:change={() => groceryStore.toggleItem(item.id)} class="h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500" />
            <span class="flex-1 truncate {item.completed ? 'line-through text-gray-400' : ''}">{item.name}</span>
            {#if item.quantity}
              <span class="text-xs text-gray-500">{item.quantity}</span>
            {/if}
            <span class="px-2 py-0.5 text-xs font-medium rounded-full ml-2 {priorityColors[item.priority]}">
              {priorityLabels[item.priority]}
            </span>
          </li>
        {/each}
      {/if}
    </ul>
  {:else}
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        Grocery List
      </h3>
      <div class="flex items-center gap-2">
        <button
          on:click={() => showAddForm = !showAddForm}
          class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          {showAddForm ? 'Cancel' : 'Add Item'}
        </button>
        {#if $completedItems.length > 0}
          <button
            on:click={handleClearCompleted}
            class="px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
          >
            Clear Completed
          </button>
        {/if}
      </div>
    </div>

    <!-- Add Item Form -->
    {#if showAddForm}
      <div class="mb-4">
        {#key addFormKey}
          <AddItemForm on:add={handleAddItem} />
        {/key}
      </div>
    {/if}

    <!-- Error Display -->
    {#if $groceryStore.error}
      <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-700 text-sm">{$groceryStore.error}</p>
        <button
          on:click={() => groceryStore.clearError()}
          class="mt-1 text-red-500 hover:text-red-700 text-xs"
        >
          Dismiss
        </button>
      </div>
    {/if}

    <!-- Loading State -->
    {#if $groceryStore.loading}
      <div class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-2 text-gray-600">Loading...</span>
      </div>
    {:else}
      <!-- Pending Items -->
      <div class="flex-1 overflow-y-auto">
        {#if $pendingItems.length === 0 && $completedItems.length === 0}
          <div class="text-center py-8 text-gray-500">
            <p class="text-lg font-medium mb-2">No grocery items yet</p>
            <p class="text-sm">Click "Add Item" to get started!</p>
          </div>
        {:else}
          <!-- Pending Items Section -->
          {#if $pendingItems.length > 0}
            <div class="mb-6">
              <h4 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                Pending ({$pendingItems.length})
              </h4>
              <div class="space-y-2">
                {#each $pendingItems as item (item.id)}
                  <GroceryItemCard
                    {item}
                    {editingItem}
                    on:edit={() => handleEditItem(item)}
                    on:update={(e) => handleUpdateItem(item.id, e.detail)}
                    on:delete={() => handleDeleteItem(item.id)}
                    on:toggle={() => handleToggleItem(item.id)}
                  />
                {/each}
              </div>
            </div>
          {/if}

          <!-- Completed Items Section -->
          {#if $completedItems.length > 0}
            <div class="mb-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-md font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                  Completed ({$completedItems.length})
                </h4>
                <button
                  on:click={() => showCompleted = !showCompleted}
                  class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
                >
                  {showCompleted ? 'Hide' : 'Show'}
                </button>
              </div>
              
              {#if showCompleted}
                <div class="space-y-2 opacity-75">
                  {#each $completedItems as item (item.id)}
                    <GroceryItemCard
                      {item}
                      {editingItem}
                      on:edit={() => handleEditItem(item)}
                      on:update={(e) => handleUpdateItem(item.id, e.detail)}
                      on:delete={() => handleDeleteItem(item.id)}
                      on:toggle={() => handleToggleItem(item.id)}
                    />
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        {/if}
      </div>

      <!-- Summary -->
      {#if $groceryStore.total_count > 0}
        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Total: {$groceryStore.total_count}</span>
            <span>Pending: {$groceryStore.pending_count}</span>
            <span>Completed: {$groceryStore.completed_count}</span>
          </div>
        </div>
      {/if}
    {/if}
  {/if}
</div>

<style>
  .grocery-list {
    min-height: 0;
  }
</style>
