<!--
  Chore Card Component
  
  Individual chore display with completion functionality.
-->

<script lang="ts">
  import { type Chore } from '$lib/stores/chores.js';

  // Props
  export let chore: Chore;
  export let status: 'available' | 'disabled' | 'pending' | 'completed';
  export let onCompleted: (() => void) | undefined = undefined;
  export let compact: boolean = false;

  function handleComplete() {
    if (onCompleted && status === 'available') {
      onCompleted();
    }
  }

  function getStatusColor(status: string): string {
    const colors = {
      available: 'border-green-200 bg-green-50',
      disabled: 'border-gray-200 bg-gray-50',
      pending: 'border-yellow-200 bg-yellow-50',
      completed: 'border-blue-200 bg-blue-50'
    };
    return colors[status as keyof typeof colors] || 'border-gray-200 bg-gray-50';
  }

  function getStatusText(status: string): string {
    const texts = {
      available: 'Available',
      disabled: 'Not Available',
      pending: 'Pending Approval',
      completed: 'Completed'
    };
    return texts[status as keyof typeof texts] || 'Unknown';
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

  function formatNextAvailable(nextAvailable: string | undefined): string {
    if (!nextAvailable) return '';
    
    const date = new Date(nextAvailable);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffHours = Math.ceil(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 24) {
      return `Available in ${diffHours}h`;
    } else {
      const diffDays = Math.ceil(diffHours / 24);
      return `Available in ${diffDays}d`;
    }
  }

  function canComplete(): boolean {
    return status === 'available' && onCompleted !== undefined;
  }
</script>

<div class="chore-card border rounded-lg p-3 {getStatusColor(status)} transition-colors hover:shadow-sm">
  <div class="flex items-start justify-between">
    <!-- Chore Info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center space-x-2 mb-1">
        <h4 class="font-medium text-gray-900 truncate">
          {chore.name}
        </h4>
        
        <!-- Points Badge -->
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
          {chore.points} pt{chore.points !== 1 ? 's' : ''}
        </span>
      </div>

      <!-- Description -->
      {#if chore.description && !compact}
        <p class="text-sm text-gray-600 mb-2 line-clamp-2">
          {chore.description}
        </p>
      {/if}

      <!-- Metadata -->
      <div class="flex items-center space-x-3 text-xs text-gray-500">
        <!-- Frequency -->
        <span class="inline-flex items-center px-2 py-0.5 rounded {getFrequencyColor(chore.frequency)}">
          {getFrequencyLabel(chore.frequency)}
        </span>

        <!-- Room -->
        {#if chore.room_name}
          <span class="truncate">
            {chore.room_name}
          </span>
        {/if}

        <!-- Completed by -->
        {#if chore.completed_by && status === 'completed'}
          <span class="truncate">
            by {chore.completed_by}
          </span>
        {/if}
      </div>

      <!-- Next Available Time -->
      {#if status === 'disabled' && chore.next_available_at}
        <div class="mt-2 text-xs text-gray-500">
          {formatNextAvailable(chore.next_available_at)}
        </div>
      {/if}
    </div>

    <!-- Action Button -->
    <div class="flex-shrink-0 ml-3">
      {#if status === 'available' && canComplete()}
        <button
          on:click={handleComplete}
          class="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Complete
        </button>
      {:else if status === 'pending'}
        <div class="inline-flex items-center px-3 py-1.5 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-lg">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Pending
        </div>
      {:else if status === 'completed'}
        <div class="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-800 text-sm font-medium rounded-lg">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Done
        </div>
      {:else if status === 'disabled'}
        <div class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Locked
        </div>
      {/if}
    </div>
  </div>

  <!-- Status Indicator -->
  <div class="mt-2 flex items-center justify-between">
    <span class="text-xs font-medium {status === 'available' ? 'text-green-700' : status === 'pending' ? 'text-yellow-700' : status === 'completed' ? 'text-blue-700' : 'text-gray-600'}">
      {getStatusText(status)}
    </span>

    <!-- Last Completed -->
    {#if chore.last_completed_at && status === 'completed'}
      <span class="text-xs text-gray-500">
        {new Date(chore.last_completed_at).toLocaleDateString()}
      </span>
    {/if}
  </div>
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
