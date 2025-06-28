<script lang="ts">
  export let open: boolean = false;
  export let onConfirm: () => void;
  export let onCancel: () => void;
</script>

<!--
Usage Example:
<SetDashboardLocationModal open={modalOpen} onConfirm={handleConfirm} onCancel={handleCancel} />
-->

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="relative">
      <div class="absolute inset-0 bg-black bg-opacity-30 rounded-xl"></div>
      <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl p-8 max-w-md w-full z-10">
        <button
          class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-2xl"
          on:click={onCancel}
          aria-label="Close"
        >&times;</button>
        <div class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Set as dashboard location?</div>
        <div class="mb-6 text-gray-600 dark:text-gray-300">
          Do you want to set this location as your dashboard's default?
        </div>
        <div class="flex gap-4 justify-end">
          <button class="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600" on:click={onCancel}>No, just view</button>
          <button class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700" on:click={onConfirm}>Yes, set as default</button>
        </div>
      </div>
    </div>
  </div>
{/if} 