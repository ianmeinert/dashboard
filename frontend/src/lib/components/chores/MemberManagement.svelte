<!--
  Member Management Component
  
  Allows parents to add and manage household members.
-->

<script lang="ts">
  import { choresStore, type HouseholdMember } from '$lib/stores/chores.js';

  // Props
  export let members: HouseholdMember[];
  export let onMemberCreated: (member: HouseholdMember) => void;
  export let onMemberUpdated: (member: HouseholdMember) => void;

  // State
  let showAddForm = false;
  let editingMember: HouseholdMember | null = null;
  let name = '';
  let dateOfBirth = '';
  let isParent = false;
  let loading = false;
  let error = '';

  function openAddForm() {
    showAddForm = true;
    editingMember = null;
    name = '';
    dateOfBirth = '';
    isParent = false;
    error = '';
  }

  function openEditForm(member: HouseholdMember) {
    editingMember = member;
    showAddForm = true;
    name = member.name;
    // Ensure date is in YYYY-MM-DD format for HTML date input
    dateOfBirth = member.date_of_birth.split('T')[0]; // Remove time part if present
    isParent = member.is_parent;
    error = '';
  }

  function closeForm() {
    showAddForm = false;
    editingMember = null;
    name = '';
    dateOfBirth = '';
    isParent = false;
    error = '';
  }

  async function handleSubmit() {
    if (!name.trim()) {
      error = 'Name is required';
      return;
    }

    if (!dateOfBirth) {
      error = 'Date of birth is required';
      return;
    }

    // Validate date of birth
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    if (birthDate >= today) {
      error = 'Date of birth must be in the past';
      return;
    }

    loading = true;
    error = '';

    try {
      const parent = $choresStore.currentParent;
      if (!parent) {
        throw new Error('No parent logged in');
      }

      if (editingMember) {
        // Update existing member
        const updatedMember = await choresStore.updateHouseholdMember(editingMember.id, {
          name: name.trim(),
          date_of_birth: dateOfBirth,
          is_parent: isParent
        });
        
        if (updatedMember) {
          onMemberUpdated(updatedMember);
          closeForm();
        }
      } else {
        // Create new member
        const newMember = await choresStore.createHouseholdMember({
          name: name.trim(),
          date_of_birth: dateOfBirth,
          is_parent: isParent
        }, parent.id);
        
        onMemberCreated(newMember);
        closeForm();
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  function getRoleColor(isParent: boolean): string {
    return isParent ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800';
  }

  function getRoleLabel(isParent: boolean): string {
    return isParent ? 'Parent' : 'Household Member';
  }
</script>

<div class="member-management">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-900">Family Members</h3>
      <p class="text-sm text-gray-600">Manage household members and their roles</p>
    </div>
    <button
      on:click={openAddForm}
      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
    >
      <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Add Member
    </button>
  </div>

  <!-- Members List -->
  {#if members.length === 0}
    <div class="text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Family Members</h3>
      <p class="text-gray-600 mb-4">Add family members to start tracking chores</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      {#each members as member (member.id)}
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-lg font-medium text-blue-600">
                  {member.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{member.name}</h4>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="text-sm text-gray-600">Age {member.age}</span>
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getRoleColor(member.is_parent)}">
                    {getRoleLabel(member.is_parent)}
                  </span>
                </div>
              </div>
            </div>
            
            <button
              on:click={() => openEditForm(member)}
              class="text-gray-400 hover:text-gray-600 transition-colors"
              title="Edit member"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
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
            {editingMember ? 'Edit Member' : 'Add Family Member'}
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
          <!-- Name -->
          <div>
            <label for="member-name" class="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              id="member-name"
              type="text"
              bind:value={name}
              placeholder="Enter member's name"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>

          <!-- Date of Birth -->
          <div>
            <label for="member-dob" class="block text-sm font-medium text-gray-700 mb-1">
              Date of Birth
            </label>
            <input
              id="member-dob"
              type="date"
              bind:value={dateOfBirth}
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>

          <!-- Is Parent Checkbox -->
          <div class="flex items-center">
            <input
              id="member-parent"
              type="checkbox"
              bind:checked={isParent}
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              disabled={loading}
            />
            <label for="member-parent" class="ml-2 block text-sm text-gray-700">
              This member is a parent
            </label>
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
                {editingMember ? 'Updating...' : 'Adding...'}
              </div>
            {:else}
              {editingMember ? 'Update Member' : 'Add Member'}
            {/if}
          </button>
        </form>
      </div>
    </div>
  {/if}
</div>
