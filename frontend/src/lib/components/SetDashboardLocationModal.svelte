<script lang="ts">
  export let open: boolean = false;
  export let onConfirm: () => void;
  export let onCancel: () => void;
  export let title: string = '';
  export let message: string = '';
</script>

<!--
Usage Example:
<SetDashboardLocationModal open={modalOpen} onConfirm={handleConfirm} onCancel={handleCancel} />
-->

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Frosted glass backdrop -->
    <div class="absolute inset-0 backdrop-blur-md bg-black/30" on:click={onCancel}></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl p-8 max-w-md w-full z-10">
      <button
        class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-2xl"
        on:click={onCancel}
        aria-label="Close"
      >&times;</button>
      <div class="mb-4 text-xl font-bold text-gray-900 dark:text-white">{title}</div>
      <div class="mb-6 text-gray-600 dark:text-gray-300">
        {message}
      </div>
      <div class="flex gap-4 justify-end">
        <button class="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600" on:click={onCancel}>No, just view</button>
        <button class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700" on:click={onConfirm}>Yes, set as default</button>
      </div>
    </div>
  </div>
{/if} 