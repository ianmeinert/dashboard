<!--
  Manage Members Modal
  
  Modal for adding and removing family members.
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { choresStore, members, ageGroups } from '$lib/stores/chores';

  const dispatch = createEventDispatcher();

  // Form state
  let showAddForm = false;
  let name = '';
  let age: number | undefined = undefined;
  let ageGroupId: number | undefined = undefined;
  let submitting = false;
  let error = '';

  // Load age groups on mount
  choresStore.loadAgeGroups();

  async function handleAddMember() {
    if (!name.trim()) {
      error = 'Name is required';
      return;
    }

    submitting = true;
    error = '';

    try {
      const response = await fetch('/api/chores/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          age,
          age_group_id: ageGroupId,
          is_active: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to add member');
      }

      // Reset form
      name = '';
      age = undefined;
      ageGroupId = undefined;
      showAddForm = false;

      // Reload members
      await choresStore.loadMembers();
      await choresStore.loadDashboard();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to add member';
    } finally {
      submitting = false;
    }
  }

  async function handleDeleteMember(memberId: number, memberName: string) {
    if (!confirm(`Are you sure you want to remove ${memberName}? This cannot be undone and will fail if they have assigned chores or completions.`)) {
      return;
    }

    try {
      const response = await fetch(`/api/chores/members/${memberId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to remove member');
      }

      // Reload members
      await choresStore.loadMembers();
      await choresStore.loadDashboard();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to remove member');
    }
  }

  function handleClose() {
    dispatch('close');
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }
</script>

<!-- Modal Backdrop -->
<div 
  class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto"
  on:click={handleBackdropClick}
  on:keydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="0"
>
  <!-- Modal Content -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full p-6 my-8" on:click|stopPropagation>
    <!-- Header -->
    <div class="flex items-start justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Manage Family Members</h3>
      <button
        on:click={handleClose}
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
        aria-label="Close"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Current Members List -->
    <div class="mb-6">
      <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Current Members</h4>
      
      {#if $members.length === 0}
        <p class="text-gray-500 text-sm">No family members yet. Add one below!</p>
      {:else}
        <div class="space-y-2">
          {#each $members as member (member.id)}
            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900 dark:text-white">{member.name}</span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {member.age_group_name} • 
                  {member.total_points} total points • 
                  {member.weekly_points}/{member.weekly_points_cap} this week
                </div>
              </div>
              
              <div class="flex items-center gap-2">
                <button
                  on:click={() => handleDeleteMember(member.id, member.name)}
                  class="px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete member"
                >
                  Delete
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Add New Member Section -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
      {#if !showAddForm}
        <button
          on:click={() => showAddForm = true}
          class="w-full px-4 py-3 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
        >
          + Add New Family Member
        </button>
      {:else}
        <div class="space-y-4">
          <h4 class="text-md font-semibold text-gray-900 dark:text-white">Add New Member</h4>
          
          <!-- Name -->
          <div>
            <label for="member-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Name <span class="text-red-500">*</span>
            </label>
            <input
              id="member-name"
              type="text"
              bind:value={name}
              required
              maxlength="100"
              placeholder="Enter name"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <!-- Age and Age Group -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="member-age" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Age
              </label>
              <input
                id="member-age"
                type="number"
                bind:value={age}
                min="0"
                max="100"
                placeholder="Optional"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label for="member-age-group" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Age Group
              </label>
              <select
                id="member-age-group"
                bind:value={ageGroupId}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value={undefined}>Select age group</option>
                {#each $ageGroups as group (group.id)}
                  <option value={group.id}>
                    {group.name} ({group.default_weekly_cap} pts/week)
                  </option>
                {/each}
              </select>
            </div>
          </div>

          <!-- Error Message -->
          {#if error}
            <div class="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-700">{error}</p>
            </div>
          {/if}

          <!-- Actions -->
          <div class="flex items-center gap-3">
            <button
              on:click={handleAddMember}
              disabled={submitting || !name.trim()}
              class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Adding...' : 'Add Member'}
            </button>
            
            <button
              on:click={() => { showAddForm = false; name = ''; age = undefined; ageGroupId = undefined; error = ''; }}
              disabled={submitting}
              class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      {/if}
    </div>

    <!-- Info Box -->
    <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
      <p class="text-sm text-blue-800 dark:text-blue-300">
        <strong>Note:</strong> You cannot delete members who have assigned chores or completion history. 
        New members are automatically set as active. To deactivate a member, use the API directly.
      </p>
    </div>
  </div>
</div>
