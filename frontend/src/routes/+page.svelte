<script lang="ts">
  import GoogleCalendarProvider from '$lib/components/calendar/GoogleCalendarProvider.svelte';
  import FamilyChores from '$lib/components/chores/FamilyChores.svelte';
  import ForecastWidget from '$lib/components/ForecastWidget.svelte';
  import GroceryList from '$lib/components/GroceryList.svelte';

  let selectedQuadrant: string | null = null;

  // Keys to force remount
  let familyCalendarKey = 0;
  let forecastWidgetKey = 0;

  let forecastWidgetRef: any;
  let dashboardForecastLocation: any = null;

  function selectQuadrant(q: string) {
    if (selectedQuadrant) return; // Prevent selecting another while focused
    selectedQuadrant = q;
    document.body.style.overflow = 'hidden';
  }
  function closeQuadrant() {
    // On close, reset calendar to current month
    if (selectedQuadrant === 'calendar') {
      familyCalendarKey += 1;
    }
    selectedQuadrant = null;
    document.body.style.overflow = '';
  }
  function refreshForecastWidget() {
    forecastWidgetKey += 1;
  }
  function handleLocationSet(event: any) {
    dashboardForecastLocation = event.detail;
    forecastWidgetKey += 1;
  }
</script>

<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
    min-height: 0;
  }
  .forecast-cell {
    grid-row: 1 / 2;
    grid-column: 1 / 2;
  }
  .grocery-cell {
    grid-row: 1 / 2;
    grid-column: 2 / 3;
  }
  .calendar-cell {
    grid-row: 2 / 3;
    grid-column: 1 / 2;
  }
  .chores-cell {
    grid-row: 2 / 3;
    grid-column: 2 / 3;
  }
  .forecast-quadrant {
    max-width: 700px;
    min-width: 420px;
    margin: 0 auto;
    /* Removed flex and min-height to allow natural growth */
  }
  .grocery-quadrant {
    /* Removed flex and min-height to allow natural stacking */
  }
  @media (max-width: 900px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
      grid-template-rows: auto auto auto auto;
    }
    .forecast-cell, .grocery-cell, .calendar-cell, .chores-cell {
      grid-column: 1 / 2;
    }
    .forecast-cell { grid-row: 1 / 2; }
    .grocery-cell { grid-row: 2 / 3; }
    .calendar-cell { grid-row: 3 / 4; }
    .chores-cell { grid-row: 4 / 5; }
  }
  .quadrant {
    transition: box-shadow 0.2s, transform 0.2s, z-index 0.2s;
    cursor: pointer;
    position: relative;
    z-index: 1;
    min-width: 0;
    overflow-wrap: break-word;
  }
  .quadrant.selected {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    margin: auto;
    z-index: 50;
    background: white;
    box-shadow: 0 0 0 9999px rgba(0,0,0,0.4), 0 8px 32px rgba(0,0,0,0.25);
    border-radius: 1rem;
    max-width: 700px;
    max-height: 90vh;
    width: 95vw;
    height: 90vh;
    display: flex;
    flex-direction: column;
    animation: popin 0.2s;
  }
  @keyframes popin {
    from { transform: scale(0.95); opacity: 0.7; }
    to { transform: scale(1); opacity: 1; }
  }
  .quadrant .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 100;
    background: #f3f4f6;
    border-radius: 9999px;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    border: none;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  .quadrant.selected,
  .quadrant.selected * {
    pointer-events: auto !important;
    user-select: auto !important;
  }
  .quadrant:not(.selected) {
    user-select: none;
  }
  .quadrant .close-btn {
    pointer-events: auto;
  }
  .quadrant-overlay {
    position: absolute;
    inset: 0;
    background: transparent;
    z-index: 10;
    cursor: pointer;
  }
</style>

<div class="min-h-screen bg-gray-50 p-4 overflow-y-auto">
  <h1 class="text-4xl font-extrabold text-center mb-8 tracking-tight">Family Dashboard</h1>
  <div class="dashboard-grid {selectedQuadrant ? 'focused' : ''}">
    <!-- Forecast (top-left) -->
    <div class="forecast-cell">
      <div class="quadrant forecast-quadrant bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md p-6 {selectedQuadrant === 'forecast' ? 'selected' : ''}" tabindex="0" aria-label="Expand Todays Forecast" on:click={() => selectQuadrant('forecast')}>
        <h2 class="text-xl font-bold mb-4 text-center">Todays Forecast</h2>
        {#key forecastWidgetKey}
          <ForecastWidget
            bind:this={forecastWidgetRef}
            on:close={closeQuadrant}
            on:defaultLocationSet={refreshForecastWidget}
            on:locationSet={handleLocationSet}
            dashboardLocation={dashboardForecastLocation}
          />
        {/key}
        {#if selectedQuadrant !== 'forecast'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'forecast'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={() => forecastWidgetRef.requestClose()}>&times;</button>
        {/if}
      </div>
    </div>

    <!-- Grocery List (top-right) -->
    <div class="grocery-cell">
      <div class="quadrant grocery-quadrant bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md p-6 {selectedQuadrant === 'grocery' ? 'selected' : ''}" tabindex="0" aria-label="Expand Grocery List" on:click={() => selectQuadrant('grocery')}>
        <h2 class="text-xl font-bold mb-4 text-center">Grocery List</h2>
        <GroceryList compact={selectedQuadrant !== 'grocery'} onShowAdd={() => selectQuadrant('grocery')} />
        {#if selectedQuadrant !== 'grocery'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'grocery'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
    </div>

    <!-- Family Calendar (bottom-left) -->
    <div class="calendar-cell">
      <div class="quadrant bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md p-6 {selectedQuadrant === 'calendar' ? 'selected' : ''}" tabindex="0" aria-label="Expand Family Calendar" on:click={() => selectQuadrant('calendar')}>
        <h2 class="text-xl font-bold mb-4 text-center">Family Calendar</h2>
        {#key `family-${familyCalendarKey}`}
          <GoogleCalendarProvider />
        {/key}
        {#if selectedQuadrant !== 'calendar'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'calendar'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
    </div>

    <!-- Family Chores (bottom-right) -->
    <div class="chores-cell">
      <div class="quadrant bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md p-6 {selectedQuadrant === 'chores' ? 'selected' : ''}" tabindex="0" aria-label="Expand Family Chores" on:click={() => selectQuadrant('chores')}>
        <h2 class="text-xl font-bold mb-4 text-center">Family Chores</h2>
        <FamilyChores compact={selectedQuadrant !== 'chores'} />
        {#if selectedQuadrant !== 'chores'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'chores'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
    </div>
  </div>
</div>
