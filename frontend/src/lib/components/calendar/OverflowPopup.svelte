<script lang="ts">
  export let events: any[] = [];
  export let date: string = '';
  export let close: () => void;
  export let openEvent: (event: any) => void;
  export let isAllDay: (event: any) => boolean;
  export let isMultiDay: (event: any) => boolean;
  export let getEventColorClass: (event: any) => string;
  export let showCloseButton: boolean = true;
</script>

<div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50" on:click={close}>
  <div class="bg-white dark:bg-gray-800 dark:text-gray-100 rounded-lg shadow-lg p-6 min-w-[300px] max-w-[90vw] relative border dark:border-gray-700" on:click|stopPropagation>
    {#if showCloseButton}
      <button
        class="absolute top-2 right-2 w-11 h-11 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 text-2xl font-bold shadow hover:bg-gray-300 dark:hover:bg-gray-600 active:bg-gray-400 dark:active:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400 border dark:border-gray-700"
        aria-label="Close popup"
        on:click={close}
        style="min-width:44px; min-height:44px;"
      >&#10005;</button>
    {/if}
    <h3 class="text-lg font-bold mb-2">Events for {date}</h3>
    <ul>
      {#each events as event (event.id)}
        <li class="mb-2">
          <div
            class={`text-xs rounded px-1 py-0.5 truncate cursor-pointer border-l-4 ${getEventColorClass(event)}
              dark:bg-opacity-80 dark:text-gray-100
              ${isAllDay(event) ? 'font-bold bg-opacity-80 border-dashed' : ''}
              ${isMultiDay(event) ? 'italic border-double' : ''}`}
            on:click={() => openEvent(event)}
            title={isAllDay(event) ? 'All-day event' : isMultiDay(event) ? 'Multi-day event' : ''}
          >
            {#if isAllDay(event)}
              <span class="inline-block align-middle mr-1 bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-1 rounded text-[10px]">All Day</span>
            {/if}
            {event.summary}
            {#if isMultiDay(event)}
              <span class="ml-1 text-[10px]">⟷</span>
            {/if}
          </div>
        </li>
      {/each}
    </ul>
    <button class="mt-4 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-800" on:click={close}>Close</button>
  </div>
</div> 