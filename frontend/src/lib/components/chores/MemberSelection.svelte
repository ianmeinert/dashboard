<!--
  Member Selection Component
  
  Allows selection of household members for chore tracking.
-->

<script lang="ts">
  import { choresStore, error, householdMembers, loading, type HouseholdMember } from '$lib/stores/chores.js';
  import { onMount } from 'svelte';

  // Props
  export let onMemberSelected: (member: HouseholdMember) => void;
  export let onClose: () => void;

  // State
  let members: HouseholdMember[] = [];
  let isLoading = false;
  let errorMessage = '';

  // Reactive statements
  $: members = $householdMembers;
  $: isLoading = $loading;
  $: errorMessage = $error;

  onMount(() => {
    // Load household members if not already loaded
    if (members.length === 0) {
      const parent = $choresStore.currentParent;
      if (parent) {
        // Parent is logged in, load members for this parent
        choresStore.loadHouseholdMembers(parent.id);
      } else {
        // No parent logged in, load all members for selection
        choresStore.loadAllHouseholdMembers();
      }
    }
  });

  function selectMember(member: HouseholdMember) {
    onMemberSelected(member);
  }

  function getRoleColor(isParent: boolean): string {
    return isParent ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800';
  }

  function getRoleLabel(isParent: boolean): string {
    return isParent ? 'Parent' : 'Household Member';
  }
</script>

<div class="member-selection">
  <div class="flex items-center justify-between mb-6">
    <h2 class="text-xl font-semibold text-gray-900">Select Family Member</h2>
    <button
      on:click={onClose}
      class="text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Close"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  {#if isLoading}
    <!-- Loading State -->
    <div class="flex items-center justify-center py-8">
      <div class="flex items-center space-x-2">
        <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600">Loading family members...</span>
      </div>
    </div>
  {:else if errorMessage}
    <!-- Error State -->
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <svg class="w-5 h-5 text-red-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-sm text-red-700 font-medium">Error loading members</p>
          <p class="text-xs text-red-600 mt-1">{errorMessage}</p>
        </div>
      </div>
    </div>
  {:else if members.length === 0}
    <!-- No Members State -->
    <div class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Family Members</h3>
      <p class="text-gray-600 mb-4">No household members have been added yet.</p>
      <p class="text-sm text-gray-500">Use the Parent Dashboard to add family members.</p>
    </div>
  {:else}
    <!-- Members List -->
    <div class="space-y-3">
      {#each members as member (member.id)}
        <button
          on:click={() => selectMember(member)}
          class="w-full p-4 text-left bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <div class="flex items-center space-x-3">
            <!-- Avatar -->
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-lg font-medium text-blue-600">
                {member.name.charAt(0).toUpperCase()}
              </span>
            </div>
            
            <!-- Member Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-medium text-gray-900 truncate">
                  {member.name}
                </h3>
              </div>
              
              <div class="flex items-center space-x-2 mt-1">
                <span class="text-sm text-gray-600">
                  Age {member.age}
                </span>
                <span class="text-gray-300">•</span>
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getRoleColor(member.is_parent)}">
                  {getRoleLabel(member.is_parent)}
                </span>
              </div>
            </div>
            
            <!-- Selection Arrow -->
            <div class="flex-shrink-0">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </button>
      {/each}
    </div>

    <!-- Instructions -->
    <div class="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex">
        <svg class="w-5 h-5 text-blue-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-sm text-blue-700 font-medium">How it works</p>
          <p class="text-xs text-blue-600 mt-1">
            Select your name to view and complete chores. You can switch members anytime.
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>
