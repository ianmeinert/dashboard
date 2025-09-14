<!--
  Room Selector Component
  
  Allows selection of rooms to filter chores.
-->

<script lang="ts">
  import { type Room } from '$lib/stores/chores.js';

  // Props
  export let rooms: Room[];
  export let selectedRoom: number | null;
  export let onRoomSelected: (roomId: number | null) => void;
  export let compact: boolean = false;

  function selectRoom(roomId: number | null) {
    onRoomSelected(roomId);
  }

  function getRoomColor(room: Room): string {
    return room.color_code || '#6B7280';
  }

  function getRoomChoreCount(roomId: number): number {
    // This would be calculated from the parent component
    // For now, we'll show a placeholder
    return 0;
  }
</script>

<div class="room-selector">
  <div class="flex items-center justify-between mb-3">
    <h3 class="text-sm font-medium text-gray-700">
      {compact ? 'Rooms' : 'Select Room'}
    </h3>
    {#if !compact}
      <span class="text-xs text-gray-500">
        {rooms.length} room{rooms.length !== 1 ? 's' : ''}
      </span>
    {/if}
  </div>

  <div class="flex flex-wrap gap-2">
    <!-- All Rooms Option -->
    <button
      on:click={() => selectRoom(null)}
      class="inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors {selectedRoom === null 
        ? 'bg-blue-100 text-blue-800 border border-blue-200' 
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'}"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
      All Rooms
    </button>

    <!-- Individual Rooms -->
    {#each rooms as room (room.id)}
      <button
        on:click={() => selectRoom(room.id)}
        class="inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors {selectedRoom === room.id 
          ? 'text-white border' 
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'}"
        style:background-color={selectedRoom === room.id ? getRoomColor(room) : undefined}
        style:border-color={selectedRoom === room.id ? getRoomColor(room) : undefined}
      >
        <div 
          class="w-3 h-3 rounded-full mr-2 {selectedRoom === room.id ? 'bg-white' : ''}"
          style:background-color={selectedRoom === room.id ? 'rgba(255,255,255,0.3)' : getRoomColor(room)}
        ></div>
        {room.name}
        {#if !compact && room.chore_count !== undefined}
          <span class="ml-1 text-xs opacity-75">
            ({room.chore_count})
          </span>
        {/if}
      </button>
    {/each}
  </div>

  {#if compact && rooms.length > 3}
    <div class="mt-2 text-xs text-gray-500">
      +{rooms.length - 3} more rooms
    </div>
  {/if}
</div>
