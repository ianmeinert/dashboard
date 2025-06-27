<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let date: string;
  export let events: CalendarEvent[] = [];
  export let isAllDay: (event: CalendarEvent) => boolean;
  export let isMultiDay: (event: CalendarEvent) => boolean;
  export let getEventColorClass: (event: CalendarEvent) => string;
  export let formatTime: (dateStr: string) => string;
  export let formatDate: (dateStr: string) => string;
  export let linkify: (text: string) => string;

  // Define CalendarEvent type
  interface CalendarEvent {
    id: string;
    summary: string;
    start: string;
    end: string;
    calendarId: string;
    calendarName: string;
    description: string;
    location: string;
  }

  function close() {
    dispatch('close');
  }

  function openEvent(event: CalendarEvent) {
    dispatch('openEvent', event);
  }

  // Sort events: all-day first, then by start time
  $: sortedEvents = events.sort((a, b) => {
    const aAllDay = isAllDay(a);
    const bAllDay = isAllDay(b);
    
    // All-day events come first
    if (aAllDay && !bAllDay) return -1;
    if (!aAllDay && bAllDay) return 1;
    
    // If both are all-day or both are timed, sort by start time
    return new Date(a.start).getTime() - new Date(b.start).getTime();
  });

  // Group events by all-day vs timed
  $: allDayEvents = sortedEvents.filter(event => {
    if (!isAllDay(event)) return false;
    const eventStart = event.start.slice(0, 10);
    const eventEnd = event.end.slice(0, 10);
    return eventStart <= date && date < eventEnd;
  });
  $: timedEvents = sortedEvents.filter(event => {
    if (isAllDay(event)) return false;
    // For timed events, check if the event occurs on this date
    // (Assume event.start and event.end are ISO strings with time)
    const eventStartDate = event.start.slice(0, 10);
    const eventEndDate = event.end.slice(0, 10);
    return eventStartDate <= date && date <= eventEndDate;
  });

  // Format the date for display
  $: displayDate = formatDate(date);
</script>

<!-- Backdrop -->
<div class="modal-backdrop"></div>
<div class="modal-container" on:click={close}>
  <div class="modal-box" on:click|stopPropagation>
    <!-- Header -->
    <div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">{displayDate}</h2>
      <button
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        on:click={close}
        aria-label="Close"
      >
        ×
      </button>
    </div>
    <!-- Content -->
    <div class="p-4 overflow-y-auto max-h-[calc(80vh-80px)]">
      {#if events.length === 0}
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
          No events scheduled for this day
        </div>
      {:else}
        <!-- All-day events section -->
        {#if allDayEvents.length > 0}
          <div class="mb-6">
            <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-3">
              All Day
            </h3>
            <div class="space-y-2">
              {#each allDayEvents as event (event.id)}
                <div class="p-3 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors" on:click={() => openEvent(event)}>
                  <div class="flex items-start justify-between">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-1">
                        <span class={`inline-block w-3 h-3 rounded-full mr-2 ${getEventColorClass(event).split(' ').find(cls => cls.startsWith('bg-'))}`}></span>
                        <h4 class="font-medium text-gray-900 dark:text-white truncate">{event.summary}</h4>
                      </div>
                      {#if event.calendarName}
                        <p class="text-sm text-gray-500 dark:text-gray-400">{event.calendarName}</p>
                      {/if}
                      {#if event.location}
                        <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">
                          📍 {event.location}
                        </p>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        <!-- Timed events section -->
        {#if timedEvents.length > 0}
          <div>
            <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-3">
              Scheduled
            </h3>
            <div class="space-y-3">
              {#each timedEvents as event (event.id)}
                <div class="p-3 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors" on:click={() => openEvent(event)}>
                  <div class="flex items-start justify-between">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-1">
                        <span class={`inline-block w-3 h-3 rounded-full mr-2 ${getEventColorClass(event).split(' ').find(cls => cls.startsWith('bg-'))}`}></span>
                        <h4 class="font-medium text-gray-900 dark:text-white truncate">{event.summary}</h4>
                      </div>
                      <div class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
                        <span>{formatTime(event.start)} - {formatTime(event.end)}</span>
                        {#if event.calendarName}
                          <span>• {event.calendarName}</span>
                        {/if}
                      </div>
                      {#if event.location}
                        <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">
                          📍 {event.location}
                        </p>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(128,128,128,0.4);
    z-index: 40;
    pointer-events: auto;
    backdrop-filter: blur(2px);
    padding-bottom: 64px;
  }
  .modal-container {
    position: fixed;
    inset: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }
  .modal-box {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18), 0 1.5px 6px rgba(0,0,0,0.08);
    max-width: 420px;
    width: 95vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    overflow: hidden;
  }
</style> 