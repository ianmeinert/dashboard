<script lang="ts">
  export let event: any;
  export let openEvent: (event: any) => void;
  export let isAllDay: (event: any) => boolean;
  export let isMultiDay: (event: any) => boolean;
  export let getEventColorClass: (event: any) => string;

  // Optionally override or extend getEventColorClass for dark mode
  function getDarkEventColorClass(event: any): string {
    // Example: map calendarId to dark bg
    if (event.calendarId && event.calendarId.includes('blue')) return 'dark:bg-blue-900 dark:text-white';
    if (event.calendarId && event.calendarId.includes('green')) return 'dark:bg-green-900 dark:text-white';
    if (event.calendarId && event.calendarId.includes('yellow')) return 'dark:bg-yellow-800 dark:text-white';
    // Default fallback
    return 'dark:bg-gray-800 dark:text-white';
  }
</script>

<div
  class={`mt-1 text-xs rounded px-1 py-0.5 truncate cursor-pointer border-l-4 
    ${getEventColorClass(event)}
    ${getDarkEventColorClass(event)}
    dark:shadow dark:ring-1 dark:ring-black/30
    ${isAllDay(event) ? 'font-bold bg-opacity-80 border-dashed' : ''}
    ${isMultiDay(event) ? 'italic border-double' : ''}`}
  on:click={() => openEvent(event)}
  title={isAllDay(event) ? 'All-day event' : isMultiDay(event) ? 'Multi-day event' : ''}
>
  {event.summary}
  {#if isMultiDay(event)}
    <span class="ml-1 text-[10px]">⟷</span>
  {/if}
</div> 