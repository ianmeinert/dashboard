<script lang="ts">
  // Define CalendarEvent interface locally
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
  
  export let cell: { day: number; month: number; year: number; isCurrent: boolean };
  export let events: CalendarEvent[] = [];
  export let isToday: boolean = false;
  export let openEvent: (event: CalendarEvent) => void;
  export let openOverflow: (cell: any) => void;
  export let openDayView: (cell: { day: number; month: number; year: number; isCurrent: boolean }) => void;
  export let maxEvents: number = 3;
</script>

<div
  class={`border min-h-[60px] p-1 rounded shadow-sm cursor-pointer transition-colors dark:border-gray-700
    ${cell.isCurrent ? 'bg-white dark:bg-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800' : 'bg-gray-100 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}
    ${isToday ? 'bg-yellow-200 dark:bg-yellow-600 border-yellow-500 dark:border-yellow-400 hover:bg-yellow-300 dark:hover:bg-yellow-500' : ''}`}
  style="position:relative;"
  on:click={() => openDayView({ ...cell })}
  on:click|stopPropagation={() => {}}
>
  <div class="font-bold">{cell.day}</div>
  {#each events.slice(0, maxEvents) as event (event.id)}
    <div on:click|stopPropagation>
      <slot name="event" {event} />
    </div>
  {/each}
  {#if events.length > maxEvents}
    <div 
      class="mt-1 text-xs text-blue-600 dark:text-blue-300 cursor-pointer underline" 
      on:click|stopPropagation={() => openOverflow(cell)}
    >
      +{events.length - maxEvents} more
    </div>
  {/if}
</div> 