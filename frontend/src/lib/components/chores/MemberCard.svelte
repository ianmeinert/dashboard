<!--
  Member Card Component
  
  Displays a family member's points, weekly progress, and stats.
-->

<script lang="ts">
  import type { FamilyMember } from '$lib/stores/chores';

  export let member: FamilyMember;

  // Calculate progress bar color based on percentage
  function getProgressColor(percent: number): string {
    if (percent >= 90) return 'bg-red-500';
    if (percent >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  }

  // Format points with animation-friendly display
  $: progressColor = getProgressColor(member.weekly_progress_percent);
  $: isNearCap = member.weekly_progress_percent >= 80;
</script>

<div class="member-card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
  <!-- Member Name & Age Group -->
  <div class="flex items-start justify-between mb-3">
    <div>
      <h5 class="font-semibold text-gray-900 dark:text-white">{member.name}</h5>
      <p class="text-xs text-gray-500 dark:text-gray-400">{member.age_group_name}</p>
    </div>
  </div>

  <!-- Weekly Progress Bar -->
  <div class="mb-3">
    <div class="flex items-center justify-between mb-1">
      <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Weekly Points</span>
      <span class="text-xs font-bold {isNearCap ? 'text-red-600' : 'text-gray-900 dark:text-white'}">
        {member.weekly_points}/{member.weekly_points_cap}
      </span>
    </div>
    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
      <div 
        class="{progressColor} h-2.5 rounded-full transition-all duration-500 ease-out"
        style="width: {Math.min(member.weekly_progress_percent, 100)}%"
      ></div>
    </div>
    <div class="flex items-center justify-between mt-1">
      <span class="text-xs text-gray-500">
        {member.weekly_points_remaining} remaining
      </span>
      <span class="text-xs font-medium text-gray-600">
        {member.weekly_progress_percent.toFixed(0)}%
      </span>
    </div>
  </div>

  <!-- Points Stats -->
  <div class="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
    <div>
      <div class="text-xs text-gray-500 dark:text-gray-400">Monthly</div>
      <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{member.monthly_points}</div>
    </div>
    <div>
      <div class="text-xs text-gray-500 dark:text-gray-400">All-Time</div>
      <div class="text-lg font-bold text-purple-600 dark:text-purple-400">{member.total_points}</div>
    </div>
  </div>

  <!-- Warning if near cap -->
  {#if isNearCap && member.weekly_points < member.weekly_points_cap}
    <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
      ⚠️ Near weekly cap! Only {member.weekly_points_remaining} points left.
    </div>
  {:else if member.weekly_points >= member.weekly_points_cap}
    <div class="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
      🚫 Weekly cap reached!
    </div>
  {/if}
</div>

<style>
  .member-card {
    transition: transform 0.2s;
  }
  
  .member-card:hover {
    transform: translateY(-2px);
  }
</style>
