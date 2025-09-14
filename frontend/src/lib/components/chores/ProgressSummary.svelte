<!--
  Progress Summary Component
  
  Shows weekly points progress and allowance information.
-->

<script lang="ts">
  // Props
  export let weeklySummary: any;
  export let allowanceSummary: any;
  export let totalChores: number;
  export let availableChores: number;
  export let completedChores: number;
  export let pendingChores: number;

  function getProgressPercentage(): number {
    if (totalChores === 0) return 0;
    return Math.round((completedChores / totalChores) * 100);
  }

  function getWeeklyProgressPercentage(): number {
    if (!weeklySummary) return 0;
    return Math.round((weeklySummary.current_week_points / weeklySummary.max_weekly_points) * 100);
  }

  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  }
</script>

<div class="progress-summary bg-white border border-gray-200 rounded-lg p-4">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Weekly Points -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-medium text-gray-700">Weekly Points</h4>
        <span class="text-xs text-gray-500">
          {weeklySummary?.current_week_points || 0}/{weeklySummary?.max_weekly_points || 30}
        </span>
      </div>
      
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div 
          class="bg-blue-600 h-2 rounded-full transition-all duration-300 {weeklySummary?.is_at_cap ? 'bg-green-600' : ''}"
          style="width: {getWeeklyProgressPercentage()}%"
        ></div>
      </div>
      
      {#if weeklySummary?.is_at_cap}
        <p class="text-xs text-green-600 font-medium">Weekly cap reached! 🎉</p>
      {:else if weeklySummary?.points_remaining !== undefined}
        <p class="text-xs text-gray-600">
          {weeklySummary.points_remaining} points remaining
        </p>
      {/if}
    </div>

    <!-- Chore Progress -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-medium text-gray-700">Chore Progress</h4>
        <span class="text-xs text-gray-500">
          {completedChores}/{totalChores}
        </span>
      </div>
      
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div 
          class="bg-green-600 h-2 rounded-full transition-all duration-300"
          style="width: {getProgressPercentage()}%"
        ></div>
      </div>
      
      <p class="text-xs text-gray-600">
        {getProgressPercentage()}% complete
      </p>
    </div>

    <!-- Available Chores -->
    <div class="space-y-2">
      <h4 class="text-sm font-medium text-gray-700">Available Now</h4>
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
          <span class="text-lg font-bold text-green-600">{availableChores}</span>
        </div>
        <div>
          <p class="text-xs text-gray-600">Ready to complete</p>
          {#if pendingChores > 0}
            <p class="text-xs text-yellow-600">{pendingChores} pending approval</p>
          {/if}
        </div>
      </div>
    </div>

    <!-- Allowance Info -->
    <div class="space-y-2">
      <h4 class="text-sm font-medium text-gray-700">Monthly Allowance</h4>
      {#if allowanceSummary}
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-lg font-bold text-green-600">
              {formatCurrency(allowanceSummary.current_month_allowance)}
            </span>
            <span class="text-xs text-gray-500">
              {Math.round(allowanceSummary.completion_percentage * 100)}%
            </span>
          </div>
          
          <div class="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              class="bg-green-600 h-1.5 rounded-full transition-all duration-300"
              style="width: {allowanceSummary.completion_percentage * 100}%"
            ></div>
          </div>
          
          <p class="text-xs text-gray-600">
            {allowanceSummary.total_points_earned}/{allowanceSummary.total_points_possible} points
          </p>
          
          <p class="text-xs text-gray-500">
            {allowanceSummary.age_category === 'adult' ? 'No allowance (adult)' : 
             allowanceSummary.age_category === 'teenager' ? `$${allowanceSummary.rate_per_point}/point` :
             `$${allowanceSummary.rate_per_point}/point`}
          </p>
        </div>
      {:else}
        <div class="text-center py-2">
          <p class="text-sm text-gray-500">No allowance data</p>
          <p class="text-xs text-gray-400">Complete chores to earn points</p>
        </div>
      {/if}
    </div>
  </div>

  <!-- Quick Stats Row -->
  <div class="mt-4 pt-3 border-t border-gray-200">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
      <div>
        <p class="text-lg font-semibold text-gray-900">{totalChores}</p>
        <p class="text-xs text-gray-500">Total Chores</p>
      </div>
      <div>
        <p class="text-lg font-semibold text-green-600">{completedChores}</p>
        <p class="text-xs text-gray-500">Completed</p>
      </div>
      <div>
        <p class="text-lg font-semibold text-yellow-600">{pendingChores}</p>
        <p class="text-xs text-gray-500">Pending</p>
      </div>
      <div>
        <p class="text-lg font-semibold text-blue-600">{availableChores}</p>
        <p class="text-xs text-gray-500">Available</p>
      </div>
    </div>
  </div>
</div>
