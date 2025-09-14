<!--
  Family Chores Component
  
  Main component for family chore tracking system.
  Handles authentication, member selection, and chore management.
-->

<script lang="ts">
  import { choresStore, currentMember, currentParent, householdMembers, isAuthenticated, type HouseholdMember, type Parent } from '$lib/stores/chores.js';
  import { onMount } from 'svelte';
  import ChoreDashboard from './ChoreDashboard.svelte';
  import MemberSelection from './MemberSelection.svelte';
  import ParentDashboard from './ParentDashboard.svelte';
  import ParentSetup from './ParentSetup.svelte';

  // Props
  export let compact: boolean = false;

  // State
  let showParentSetup = false;
  let showMemberSelection = false;
  let showParentDashboard = false;
  let parentSetupMode: 'create' | 'login' = 'create';
  let parent: Parent | null = null;
  let members: HouseholdMember[] = [];
  let currentUser: HouseholdMember | null = null;
  let isLoggedIn = false;

  // Reactive statements
  $: parent = $currentParent;
  $: members = $householdMembers;
  $: currentUser = $currentMember;
  $: isLoggedIn = $isAuthenticated;

  onMount(async () => {
    // Check if there's a stored parent session
    const storedParent = localStorage.getItem('chores_parent');
    if (storedParent) {
      try {
        const parentData = JSON.parse(storedParent);
        choresStore.setCurrentParent(parentData);
        await choresStore.initializeParentData(parentData.id);
      } catch (error) {
        console.error('Failed to restore parent session:', error);
        localStorage.removeItem('chores_parent');
      }
    } else {
      // Check if any parents exist in the system
      try {
        const response = await choresStore.checkParentsExist();
        if (!response.exists) {
          // No parents exist, show setup option
          showParentSetup = true;
          parentSetupMode = 'create';
        }
        // If parents exist, don't show anything - user can click login button
      } catch (error) {
        console.error('Failed to check for existing parents:', error);
        // On error, assume parents might exist and don't show setup
      }
    }
  });

  function handleParentCreated(parentData: Parent) {
    parent = parentData;
    localStorage.setItem('chores_parent', JSON.stringify(parentData));
    showParentSetup = false;
    choresStore.initializeParentData(parentData.id);
  }

  function handleParentVerified(parentData: Parent) {
    parent = parentData;
    localStorage.setItem('chores_parent', JSON.stringify(parentData));
    showParentSetup = false;
    choresStore.initializeParentData(parentData.id);
  }

  function handleMemberSelected(member: HouseholdMember) {
    currentUser = member;
    choresStore.setCurrentMember(member);
    showMemberSelection = false;
  }

  function handleLogout() {
    choresStore.logout();
    localStorage.removeItem('chores_parent');
    parent = null;
    currentUser = null;
    showParentDashboard = false;
  }

  function showParentSetupModal() {
    parentSetupMode = 'create';
    showParentSetup = true;
  }

  function showParentLoginModal() {
    parentSetupMode = 'login';
    showParentSetup = true;
  }

  function showMemberSelectionModal() {
    showMemberSelection = true;
  }

  function showParentDashboardModal() {
    showParentDashboard = true;
  }

  function closeModals() {
    showParentSetup = false;
    showMemberSelection = false;
    showParentDashboard = false;
  }
</script>

<div class="family-chores h-full flex flex-col">
  {#if !isLoggedIn}
    <!-- No parent logged in - show appropriate options -->
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="mb-6">
          <div class="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Family Chores</h3>
          <p class="text-gray-600 mb-6">Manage household chores and track allowances</p>
        </div>
        
        <div class="space-y-3">
          <button
            on:click={showParentLoginModal}
            class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Parent Login
          </button>
          
          <button
            on:click={showParentSetupModal}
            class="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Set Up Parent Account
          </button>
        </div>
      </div>
    </div>
  {:else if !currentUser}
    <!-- Parent logged in but no member selected -->
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="mb-6">
          <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Select Family Member</h3>
          <p class="text-gray-600 mb-6">Choose who you are to view and complete chores</p>
        </div>
        
        <div class="space-y-3">
          <button
            on:click={showMemberSelectionModal}
            class="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Select Family Member
          </button>
          
          <button
            on:click={showParentDashboardModal}
            class="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Parent Dashboard
          </button>
        </div>
      </div>
    </div>
  {:else}
    <!-- Member selected - show chore dashboard -->
    <div class="flex-1 flex flex-col">
      <!-- Header with member info and logout -->
      <div class="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <span class="text-sm font-medium text-blue-600">
              {currentUser.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 class="font-medium text-gray-900">{currentUser.name}</h3>
            <p class="text-sm text-gray-500">
              {currentUser.age_category === 'adult' ? 'Adult' : 
               currentUser.age_category === 'teenager' ? 'Teenager' : 
               currentUser.age_category === 'preteen' ? 'Preteen' : 'Child'}
            </p>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            on:click={showParentDashboardModal}
            class="text-sm text-gray-600 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100"
            title="Parent Dashboard"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          
          <button
            on:click={handleLogout}
            class="text-sm text-gray-600 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100"
            title="Logout"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Chore Dashboard -->
      <ChoreDashboard {compact} />
    </div>
  {/if}

  <!-- Modals -->
  {#if showParentSetup}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeModals}>
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" on:click|stopPropagation>
        <ParentSetup
          mode={parentSetupMode}
          onParentCreated={handleParentCreated}
          onParentVerified={handleParentVerified}
          onClose={closeModals}
        />
      </div>
    </div>
  {/if}

  {#if showMemberSelection}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeModals}>
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" on:click|stopPropagation>
        <MemberSelection
          onMemberSelected={handleMemberSelected}
          onClose={closeModals}
        />
      </div>
    </div>
  {/if}

  {#if showParentDashboard}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeModals}>
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" on:click|stopPropagation>
        <ParentDashboard onClose={closeModals} />
      </div>
    </div>
  {/if}
</div>

<style>
  .family-chores {
    min-height: 0;
  }
</style>
