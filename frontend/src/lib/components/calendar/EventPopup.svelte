<script lang="ts">
  export let event: any;
  export let close: () => void;
  export let isAllDay: (event: any) => boolean;
  export let isMultiDay: (event: any) => boolean;
  export let formatDate: (dateStr: string) => string;
  export let formatTime: (dateStr: string) => string;
  export let getEventColorClass: (event: any) => string;
  export let linkify: (text: string) => string;
  export let showCloseButton: boolean = true;
  export let dayEvents: any[] = [];
</script>

<div class="modal-backdrop"></div>
<div class="modal-container modal-popup" on:click={close}>
  <div class="modal-box" on:click|stopPropagation>
    {#if showCloseButton}
      <button
        class="absolute top-2 right-2 w-11 h-11 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 text-2xl font-bold shadow hover:bg-gray-300 dark:hover:bg-gray-600 active:bg-gray-400 dark:active:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400 border dark:border-gray-700"
        aria-label="Close popup"
        on:click={close}
        style="min-width:44px; min-height:44px;"
      >&#10005;</button>
    {/if}
    <h3 class="text-lg font-bold mb-2">{event.summary}</h3>
    <div class="mb-1">
      <span class="font-semibold">When:</span>
      {#if isMultiDay(event)}
        {event.start.slice(0, 10)} to {event.end.slice(0, 10)}
      {:else if isAllDay(event)}
        All day, {event.start.slice(0, 10)}
      {:else if event.start.slice(0, 10) === event.end.slice(0, 10)}
        {formatDate(event.start)}, {formatTime(event.start)} – {formatTime(event.end)}
      {:else}
        {event.start} – {event.end}
      {/if}
    </div>
    {#if event.location}
      <div class="mb-1">
        <span class="font-semibold">Location:</span>
        <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(event.location)}`} target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-300 underline">{event.location}</a>
      </div>
    {/if}
    {#if event.description}
      <div class="mb-1">
        <span class="font-semibold">Description:</span>
        <div class="whitespace-pre-line">
          {@html linkify(event.description)}
        </div>
      </div>
    {/if}
    <div class="mb-1 flex items-center gap-2">
      <span class="font-semibold">Calendar:</span>
      <span class={`inline-block w-3 h-3 rounded-full ${getEventColorClass(event)}`}></span>
      {event.calendarName}
    </div>
    <button class="mt-4 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-800" on:click={close}>Close</button>
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
  .modal-popup {
    z-index: 70;
  }
  .modal-box {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18), 0 1.5px 6px rgba(0,0,0,0.08);
    max-width: 340px;
    width: 95vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    overflow: hidden;
    position: relative;
    padding: 2rem 1.5rem 1.5rem 1.5rem;
  }
</style> 