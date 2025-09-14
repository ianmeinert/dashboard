<!--
  Chore Management Component
  
  Allows parents to add and manage chores.
-->

<script lang="ts">
  import { choresStore, type Chore, type Room } from '$lib/stores/chores.js';

  // Props
  export let chores: Chore[];
  export let rooms: Room[];
  export let onChoreCreated: (chore: Chore) => void;
  export let onChoreUpdated: (chore: Chore) => void;

  // State
  let showAddForm = false;
  let editingChore: Chore | null = null;
  let name = '';
  let description = '';
  let points = 1;
  let frequency = 'daily';
  let roomId = 0;
  let loading = false;
  let error = '';

  const frequencyOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' }
  ];

  function openAddForm() {
    showAddForm = true;
    editingChore = null;
    name = '';
    description = '';
    points = 1;
    frequency = 'daily';
    roomId = rooms.length > 0 ? rooms[0].id : 0;
    error = '';
  }

  function openEditForm(chore: Chore) {
    editingChore = chore;
    showAddForm = true;
    name = chore.name;
    description = chore.description || '';
    points = chore.points;
    frequency = chore.frequency;
    roomId = chore.room_id;
    error = '';
  }

  function closeForm() {
    showAddForm = false;
    editingChore = null;
    name = '';
    description = '';
    points = 1;
    frequency = 'daily';
    roomId = 0;
    error = '';
  }

  async function handleSubmit() {
    if (!name.trim()) {
      error = 'Chore name is required';
      return;
    }

    if (points < 1 || points > 100) {
      error = 'Points must be between 1 and 100';
      return;
    }

    if (!roomId) {
      error = 'Please select a room';
      return;
    }

    loading = true;
    error = '';

    try {
      const parent = $choresStore.currentParent;
      if (!parent) {
        throw new Error('No parent logged in');
      }

      if (editingChore) {
        // Update existing chore
        const updatedChore = await choresStore.updateChore(editingChore.id, {
          name: name.trim(),
          description: description.trim() || undefined,
          points: points,
          frequency: frequency as 'daily' | 'weekly' | 'monthly'
        });
        
        if (updatedChore) {
          onChoreUpdated(updatedChore);
          closeForm();
        }
      } else {
        // Create new chore
        const newChore = await choresStore.createChore({
          name: name.trim(),
          description: description.trim() || undefined,
          points: points,
          frequency: frequency as 'daily' | 'weekly' | 'monthly',
          room_id: roomId
        }, parent.id);
        
        onChoreCreated(newChore);
        closeForm();
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  async function handleDelete(chore: Chore) {
    if (confirm(`Are you sure you want to delete "${chore.name}"?`)) {
      try {
        await choresStore.deleteChore(chore.id);
        // Chore will be removed from the store automatically
      } catch (err) {
        error = err instanceof Error ? err.message : 'Failed to delete chore';
      }
    }
  }

  function getFrequencyColor(frequency: string): string {
    const colors = {
      daily: 'bg-blue-100 text-blue-800',
      weekly: 'bg-green-100 text-green-800',
      monthly: 'bg-purple-100 text-purple-800'
    };
    return colors[frequency as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  }

  function getFrequencyLabel(frequency: string): string {
    const labels = {
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly'
    };
    return labels[frequency as keyof typeof labels] || frequency;
  }

  function getRoomName(roomId: number): string {
    const room = rooms.find(r => r.id === roomId);
    return room ? room.name : 'Unknown Room';
  }

  function getRoomColor(roomId: number): string {
    const room = rooms.find(r => r.id === roomId);
    return room ? (room.color_code || '#6B7280') : '#6B7280';
  }
</script>

<div class="chore-management">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900">Chores</h3>
      <p class="text-sm text-gray-600">Manage household chores and their details</p>
    </div>
    <button
      on:click={openAddForm}
      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      disabled={rooms.length === 0}
    >
      <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Add Chore
    </button>
  </div>

  {#if rooms.length === 0}
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div class="flex">
        <svg class="w-5 h-5 text-yellow-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <div>
          <p class="text-sm text-yellow-700 font-medium">No Rooms Available</p>
          <p class="text-xs text-yellow-600 mt-1">Add rooms first before creating chores.</p>
        </div>
      </div>
    </div>
  {:else if chores.length === 0}
    <div class="text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Chores Added</h3>
      <p class="text-gray-600 mb-4">Add chores to start tracking family tasks</p>
    </div>
  {:else}
    <!-- Chores List -->
    <div class="space-y-4">
      {#each chores as chore (chore.id)}
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3 mb-2">
                <div 
                  class="w-3 h-3 rounded-full flex-shrink-0"
                  style="background-color: {getRoomColor(chore.room_id)}"
                ></div>
                <h4 class="font-medium text-gray-900">{chore.name}</h4>
                
                <!-- Points Badge -->
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  {chore.points} pt{chore.points !== 1 ? 's' : ''}
                </span>
                
                <!-- Frequency Badge -->
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getFrequencyColor(chore.frequency)}">
                  {getFrequencyLabel(chore.frequency)}
                </span>
              </div>
              
              {#if chore.description}
                <p class="text-sm text-gray-600 mb-2 line-clamp-2">{chore.description}</p>
              {/if}
              
              <div class="flex items-center space-x-4 text-xs text-gray-500">
                <span>{getRoomName(chore.room_id)}</span>
                <span>Created {new Date(chore.created_at).toLocaleDateString()}</span>
                {#if chore.last_completed_at}
                  <span>Last completed {new Date(chore.last_completed_at).toLocaleDateString()}</span>
                {/if}
              </div>
            </div>
            
            <div class="flex items-center space-x-1 ml-4">
              <button
                on:click={() => openEditForm(chore)}
                class="text-gray-400 hover:text-gray-600 transition-colors p-1"
                title="Edit chore"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              
              <button
                on:click={() => handleDelete(chore)}
                class="text-gray-400 hover:text-red-600 transition-colors p-1"
                title="Delete chore"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Add/Edit Form Modal -->
  {#if showAddForm}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeForm}>
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" on:click|stopPropagation>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {editingChore ? 'Edit Chore' : 'Add Chore'}
          </h3>
          <button
            on:click={closeForm}
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form on:submit|preventDefault={handleSubmit} class="space-y-4">
          <!-- Chore Name -->
          <div>
            <label for="chore-name" class="block text-sm font-medium text-gray-700 mb-1">
              Chore Name
            </label>
            <input
              id="chore-name"
              type="text"
              bind:value={name}
              placeholder="e.g., Take out trash, Vacuum living room"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>

          <!-- Description -->
          <div>
            <label for="chore-description" class="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              id="chore-description"
              bind:value={description}
              placeholder="Additional details about this chore"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            ></textarea>
          </div>

          <!-- Room Selection -->
          <div>
            <label for="chore-room" class="block text-sm font-medium text-gray-700 mb-1">
              Room
            </label>
            <select
              id="chore-room"
              bind:value={roomId}
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            >
              {#each rooms as room}
                <option value={room.id}>{room.name}</option>
              {/each}
            </select>
          </div>

          <!-- Points and Frequency -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="chore-points" class="block text-sm font-medium text-gray-700 mb-1">
                Points
              </label>
              <input
                id="chore-points"
                type="number"
                bind:value={points}
                min="1"
                max="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label for="chore-frequency" class="block text-sm font-medium text-gray-700 mb-1">
                Frequency
              </label>
              <select
                id="chore-frequency"
                bind:value={frequency}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loading}
              >
                {#each frequencyOptions as option}
                  <option value={option.value}>{option.label}</option>
                {/each}
              </select>
            </div>
          </div>

          <!-- Error Message -->
          {#if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-3">
              <div class="flex">
                <svg class="w-5 h-5 text-red-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-red-700">{error}</p>
              </div>
            </div>
          {/if}

          <!-- Submit Button -->
          <button
            type="submit"
            disabled={loading}
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {#if loading}
              <div class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {editingChore ? 'Updating...' : 'Adding...'}
              </div>
            {:else}
              {editingChore ? 'Update Chore' : 'Add Chore'}
            {/if}
          </button>
        </form>
      </div>
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
