<!--
  Pending Approvals Component
  
  Shows chores that need parent approval.
-->

<script lang="ts">
  import { type ChoreCompletion } from '$lib/stores/chores.js';

  // Props
  export let completions: ChoreCompletion[];
  export let onApproved: (completionId: number) => void;

  function handleApprove(completionId: number) {
    onApproved(completionId);
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="pending-approvals">
  {#if completions.length === 0}
    <!-- No Pending Approvals -->
    <div class="text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">All Caught Up!</h3>
      <p class="text-gray-600">No chores are waiting for your approval.</p>
    </div>
  {:else}
    <!-- Pending Completions List -->
    <div class="space-y-4">
      {#each completions as completion (completion.id)}
        <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <!-- Completion Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3 mb-2">
                <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-blue-600">
                    {completion.member_name?.charAt(0).toUpperCase() || '?'}
                  </span>
                </div>
                <div>
                  <h4 class="font-medium text-gray-900">
                    {completion.chore_name || 'Unknown Chore'}
                  </h4>
                  <p class="text-sm text-gray-600">
                    Completed by {completion.member_name || 'Unknown Member'}
                  </p>
                </div>
              </div>

              <!-- Points and Date -->
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {completion.points_earned} point{completion.points_earned !== 1 ? 's' : ''}
                </span>
                <span>
                  Completed {formatDate(completion.created_at)}
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center space-x-2 ml-4">
              <button
                on:click={() => handleApprove(completion.id)}
                class="inline-flex items-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Approve
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Summary -->
    <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-blue-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-sm text-blue-700 font-medium">
            {completions.length} chore{completions.length !== 1 ? 's' : ''} waiting for approval
          </p>
          <p class="text-xs text-blue-600 mt-1">
            Click "Approve" to confirm completed chores and award points.
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>
