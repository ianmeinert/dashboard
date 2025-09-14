<!--
  Room Management Component
  
  Allows parents to add and manage rooms for organizing chores.
-->

<script lang="ts">
  import { choresStore, type Room } from '$lib/stores/chores.js';

  // Props
  export let rooms: Room[];
  export let onRoomCreated: (room: Room) => void;
  export let onRoomUpdated: (room: Room) => void;

  // State
  let showAddForm = false;
  let editingRoom: Room | null = null;
  let name = '';
  let description = '';
  let colorCode = '#6B7280';
  let loading = false;
  let error = '';

  const predefinedColors = [
    '#6B7280', '#EF4444', '#F97316', '#F59E0B', '#10B981', 
    '#06B6D4', '#3B82F6', '#8B5CF6', '#EC4899', '#84CC16'
  ];

  function openAddForm() {
    showAddForm = true;
    editingRoom = null;
    name = '';
    description = '';
    colorCode = '#6B7280';
    error = '';
  }

  function openEditForm(room: Room) {
    editingRoom = room;
    showAddForm = true;
    name = room.name;
    description = room.description || '';
    colorCode = room.color_code || '#6B7280';
    error = '';
  }

  function closeForm() {
    showAddForm = false;
    editingRoom = null;
    name = '';
    description = '';
    colorCode = '#6B7280';
    error = '';
  }

  async function handleSubmit() {
    if (!name.trim()) {
      error = 'Room name is required';
      return;
    }

    loading = true;
    error = '';

    try {
      const parent = $choresStore.currentParent;
      if (!parent) {
        throw new Error('No parent logged in');
      }

      if (editingRoom) {
        // Update existing room
        const updatedRoom = await choresStore.updateRoom(editingRoom.id, {
          name: name.trim(),
          description: description.trim() || undefined,
          color_code: colorCode
        });
        
        if (updatedRoom) {
          onRoomUpdated(updatedRoom);
          closeForm();
        }
      } else {
        // Create new room
        const newRoom = await choresStore.createRoom({
          name: name.trim(),
          description: description.trim() || undefined,
          color_code: colorCode
        }, parent.id);
        
        onRoomCreated(newRoom);
        closeForm();
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  async function handleDelete(room: Room) {
    if (confirm(`Are you sure you want to delete "${room.name}"? This will also delete all chores in this room.`)) {
      try {
        await choresStore.deleteRoom(room.id);
        // Room will be removed from the store automatically
      } catch (err) {
        error = err instanceof Error ? err.message : 'Failed to delete room';
      }
    }
  }
</script>

<div class="room-management">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900">Rooms</h3>
      <p class="text-sm text-gray-600">Organize chores by room or area</p>
    </div>
    <button
      on:click={openAddForm}
      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
    >
      <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Add Room
    </button>
  </div>

  <!-- Rooms Grid -->
  {#if rooms.length === 0}
    <div class="text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Rooms Added</h3>
      <p class="text-gray-600 mb-4">Add rooms to organize your family's chores</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each rooms as room (room.id)}
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div 
                class="w-4 h-4 rounded-full flex-shrink-0"
                style="background-color: {room.color_code || '#6B7280'}"
              ></div>
              <h4 class="font-medium text-gray-900">{room.name}</h4>
            </div>
            
            <div class="flex items-center space-x-1">
              <button
                on:click={() => openEditForm(room)}
                class="text-gray-400 hover:text-gray-600 transition-colors p-1"
                title="Edit room"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              
              <button
                on:click={() => handleDelete(room)}
                class="text-gray-400 hover:text-red-600 transition-colors p-1"
                title="Delete room"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
          
          {#if room.description}
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{room.description}</p>
          {/if}
          
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>
              {room.chore_count || 0} chore{(room.chore_count || 0) !== 1 ? 's' : ''}
            </span>
            <span>
              Added {new Date(room.created_at).toLocaleDateString()}
            </span>
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
            {editingRoom ? 'Edit Room' : 'Add Room'}
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
          <!-- Room Name -->
          <div>
            <label for="room-name" class="block text-sm font-medium text-gray-700 mb-1">
              Room Name
            </label>
            <input
              id="room-name"
              type="text"
              bind:value={name}
              placeholder="e.g., Kitchen, Living Room, Bathroom"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>

          <!-- Description -->
          <div>
            <label for="room-description" class="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              id="room-description"
              bind:value={description}
              placeholder="Brief description of this room or area"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            ></textarea>
          </div>

          <!-- Color Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Color
            </label>
            <div class="flex flex-wrap gap-2">
              {#each predefinedColors as color}
                <button
                  type="button"
                  on:click={() => colorCode = color}
                  class="w-8 h-8 rounded-full border-2 {colorCode === color ? 'border-gray-400' : 'border-gray-200'} hover:border-gray-300 transition-colors"
                  style="background-color: {color}"
                  title="Select {color}"
                ></button>
              {/each}
            </div>
            <div class="mt-2 flex items-center space-x-2">
              <input
                type="color"
                bind:value={colorCode}
                class="w-8 h-8 rounded border border-gray-300"
                disabled={loading}
              />
              <span class="text-sm text-gray-600">Custom color</span>
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
                {editingRoom ? 'Updating...' : 'Adding...'}
              </div>
            {:else}
              {editingRoom ? 'Update Room' : 'Add Room'}
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
