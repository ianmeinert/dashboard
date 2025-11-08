<!--
  Chores Dashboard Component
  
  Main dashboard for the chores system showing family members, their points,
  and active chores. Designed to be displayed as a quadrant in the main dashboard.
-->

<script lang="ts">
  import { choresError, choresLoading, choresStore, dashboardData, members } from '$lib/stores/chores';
  import { onMount } from 'svelte';
  import ChoresList from './ChoresList.svelte';
  import ManageMembersModal from './ManageMembersModal.svelte';
  import MemberCard from './MemberCard.svelte';

  export let compact: boolean = false;

  let showManageMembersModal = false;

  // Load dashboard data on mount
  onMount(() => {
    choresStore.loadDashboard();
    choresStore.loadChores();
  });

  // Auto-refresh every 5 minutes
  let refreshInterval: number;
  onMount(() => {
    refreshInterval = setInterval(() => {
      choresStore.loadDashboard();
      choresStore.loadChores();
    }, 5 * 60 * 1000);

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  });

  function handleRefresh() {
    choresStore.loadDashboard();
    choresStore.loadChores();
  }
</script>

<div class="chores-dashboard h-full flex flex-col">
  {#if compact}
    <!-- Compact View -->
    <div class="space-y-4">
      {#if $choresLoading}
        <div class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-2 text-gray-600">Loading...</span>
        </div>
      {:else if $dashboardData}
        <!-- Quick Stats -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-blue-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-blue-600">{$dashboardData.actionable_chores}</div>
            <div class="text-sm text-gray-600">Actionable</div>
          </div>
          <div class="bg-green-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-green-600">{$dashboardData.completed_today}</div>
            <div class="text-sm text-gray-600">Done Today</div>
          </div>
        </div>

        <!-- Top Members (showing weekly progress) -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-2">Weekly Progress</h4>
          <div class="space-y-2">
            {#each $members.slice(0, 5) as member (member.id)}
              <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span class="text-sm font-medium">{member.name}</span>
                <div class="flex items-center gap-2">
                  <div class="text-xs text-gray-600">
                    {member.weekly_points}/{member.weekly_points_cap}
                  </div>
                  <div class="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-blue-600 h-2 rounded-full transition-all"
                      style="width: {member.weekly_progress_percent}%"
                    ></div>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <!-- Full View -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        Chores Dashboard
      </h3>
      <div class="flex items-center gap-2">
        <button
          on:click={() => showManageMembersModal = true}
          class="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          👥 Manage Members
        </button>
        <button
          on:click={handleRefresh}
          class="px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
          disabled={$choresLoading}
        >
          {$choresLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
    </div>

    <!-- Error Display -->
    {#if $choresError}
      <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-700 text-sm">{$choresError}</p>
        <button
          on:click={() => choresStore.clearError()}
          class="mt-1 text-red-500 hover:text-red-700 text-xs"
        >
          Dismiss
        </button>
      </div>
    {/if}

    <!-- Loading State -->
    {#if $choresLoading && !$dashboardData}
      <div class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-2 text-gray-600">Loading chores...</span>
      </div>
    {:else if $dashboardData}
      <!-- Dashboard Stats -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="bg-blue-50 rounded-lg p-4">
          <div class="text-3xl font-bold text-blue-600">{$dashboardData.actionable_chores}</div>
          <div class="text-sm text-gray-600">Actionable Chores</div>
        </div>
        <div class="bg-green-50 rounded-lg p-4">
          <div class="text-3xl font-bold text-green-600">{$dashboardData.completed_today}</div>
          <div class="text-sm text-gray-600">Completed Today</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-4">
          <div class="text-3xl font-bold text-purple-600">{$dashboardData.completed_chores}</div>
          <div class="text-sm text-gray-600">Total Completed</div>
        </div>
        <div class="bg-orange-50 rounded-lg p-4">
          <div class="text-3xl font-bold text-orange-600">{$members.length}</div>
          <div class="text-sm text-gray-600">Family Members</div>
        </div>
      </div>

      <!-- Family Members Section -->
      <div class="mb-6">
        <h4 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
          Family Members
        </h4>
        <!-- Horizontal scroll container -->
        <div class="overflow-x-auto pb-2">
          <div class="flex gap-4 min-w-max">
            {#each $members as member (member.id)}
              <div class="flex-shrink-0 w-64">
                <MemberCard {member} />
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Active Chores Section -->
      <div class="flex-1 overflow-y-auto">
        <h4 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
          Active Chores
        </h4>
        <ChoresList />
      </div>
    {/if}
  {/if}
</div>

<!-- Manage Members Modal -->
{#if showManageMembersModal}
  <ManageMembersModal
    on:close={() => showManageMembersModal = false}
  />
{/if}

<style>
  .chores-dashboard {
    min-height: 0;
  }

  /* Custom scrollbar styling for member cards */
  .overflow-x-auto {
    scrollbar-width: thin;
    scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
  }

  .overflow-x-auto::-webkit-scrollbar {
    height: 6px;
  }

  .overflow-x-auto::-webkit-scrollbar-track {
    background: transparent;
  }

  .overflow-x-auto::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 3px;
  }

  .overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
  }
</style>
