<script lang="ts">
  import Calendar from '$lib/components/calendar/Calendar.svelte';
  import GoogleCalendarProvider from '$lib/components/calendar/GoogleCalendarProvider.svelte';

  let selectedQuadrant: string | null = null;

  // Keys to force remount
  let familyCalendarKey = 0;
  let choresCalendarKey = 0;

  // For initial month/year
  let now = new Date();
  let familyInitialYear = now.getFullYear();
  let familyInitialMonth = now.getMonth();
  let choresInitialYear = now.getFullYear();
  let choresInitialMonth = now.getMonth();

  function selectQuadrant(q: string) {
    if (selectedQuadrant) return; // Prevent selecting another while focused
    selectedQuadrant = q;
    document.body.style.overflow = 'hidden';
  }
  function closeQuadrant() {
    // On close, reset calendars to current month
    now = new Date();
    if (selectedQuadrant === 'calendar') {
      familyCalendarKey += 1;
      familyInitialYear = now.getFullYear();
      familyInitialMonth = now.getMonth();
    }
    if (selectedQuadrant === 'chores') {
      choresCalendarKey += 1;
      choresInitialYear = now.getFullYear();
      choresInitialMonth = now.getMonth();
    }
    selectedQuadrant = null;
    document.body.style.overflow = '';
  }
</script>

<style>
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
    min-height: 80vh;
  }
  .calendar-cell {
    grid-row: 1 / 2;
    grid-column: 1 / 2;
  }
  .forecast-cell {
    grid-row: 1 / 2;
    grid-column: 2 / 2;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  .forecast-quadrant {
    flex: 1 1 0;
    min-height: 0;
  }
  .grocery-quadrant {
    flex: 1 1 0;
    min-height: 0;
  }
  .chores-cell {
    grid-row: 2 / 3;
    grid-column: 1 / 3;
  }
  @media (max-width: 900px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
      grid-template-rows: auto auto auto auto;
    }
    .calendar-cell, .forecast-cell, .chores-cell {
      grid-column: 1 / 2;
    }
    .chores-cell {
      grid-row: 4 / 5;
    }
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

<div class="min-h-screen bg-gray-50 p-4">
  <div class="dashboard-grid {selectedQuadrant ? 'focused' : ''}">
    <!-- Family Calendar -->
    <div class="calendar-cell">
      <div class="quadrant {selectedQuadrant === 'calendar' ? 'selected' : ''}" tabindex="0" aria-label="Expand Family Calendar" on:click={() => selectQuadrant('calendar')}>
        <h2 class="text-xl font-bold mb-4 text-center">Family Calendar</h2>
        {#key `family-${familyCalendarKey}`}
          <GoogleCalendarProvider initialYear={familyInitialYear} initialMonth={familyInitialMonth} />
        {/key}
        {#if selectedQuadrant !== 'calendar'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'calendar'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
    </div>

    <!-- Forecast & Grocery List split vertically -->
    <div class="forecast-cell">
      <div class="quadrant forecast-quadrant {selectedQuadrant === 'forecast' ? 'selected' : ''}" tabindex="0" aria-label="Expand Todays Forecast" on:click={() => selectQuadrant('forecast')}>
        <h2 class="text-xl font-bold mb-4 text-center">Todays Forecast</h2>
        <div class="flex-1 flex items-center justify-center text-gray-400">Weather widget coming soon…</div>
        {#if selectedQuadrant !== 'forecast'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'forecast'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
      <div class="quadrant grocery-quadrant {selectedQuadrant === 'grocery' ? 'selected' : ''}" tabindex="0" aria-label="Expand Grocery List" on:click={() => selectQuadrant('grocery')}>
        <h2 class="text-xl font-bold mb-4 text-center">Grocery List</h2>
        <div class="flex-1 flex items-center justify-center text-gray-400">Grocery list coming soon…</div>
        {#if selectedQuadrant !== 'grocery'}
          <div class="quadrant-overlay" tabindex="-1" aria-hidden="true"></div>
        {/if}
        {#if selectedQuadrant === 'grocery'}
          <button class="close-btn" aria-label="Close" on:click|stopPropagation={closeQuadrant}>&times;</button>
        {/if}
      </div>
    </div>

    <!-- Family Chores (full width bottom) -->
    <div class="chores-cell">
      <div class="quadrant {selectedQuadrant === 'chores' ? 'selected' : ''}" tabindex="0" aria-label="Expand Family Chores" on:click={() => selectQuadrant('chores')}>
        <h2 class="text-xl font-bold mb-4 text-center">Family Chores</h2>
        {#key `chores-${choresCalendarKey}`}
          <Calendar initialYear={choresInitialYear} initialMonth={choresInitialMonth} />
        {/key}
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
