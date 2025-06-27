<script lang="ts">
  export let calendarIds: string[] = [];
  export let calendarColors: Record<string, string> = {};
  export let calendarNames: Record<string, string> = {};
</script>

<div class="flex flex-wrap gap-4 mt-4 dark:bg-gray-800 p-2 rounded-lg dark:text-gray-200">
  {#each calendarIds as id}
    <div class="flex items-center gap-2">
      <span class={`inline-block w-5 h-5 rounded-full mr-2 ${calendarColors[id]}`}></span>
      <span class="text-xs">{calendarNames[id] || id}</span>
    </div>
  {/each}
</div> 