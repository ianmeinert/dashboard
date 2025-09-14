<!--
  Parent Setup Component
  
  Handles parent account creation and login with PIN authentication.
-->

<script lang="ts">
  import { choresStore, type Parent } from '$lib/stores/chores.js';

  // Props
  export let mode: 'create' | 'login' = 'create';
  export let onParentCreated: (parent: Parent) => void;
  export let onParentVerified: (parent: Parent) => void;
  export let onClose: () => void;

  // State
  let currentMode: 'create' | 'login' = mode;
  let name = '';
  let pin = '';
  let confirmPin = '';
  let loading = false;
  let error = '';

  // Sync currentMode with prop changes
  $: currentMode = mode;

  function switchMode(newMode: 'create' | 'login') {
    currentMode = newMode;
    name = '';
    pin = '';
    confirmPin = '';
    error = '';
  }

  async function handleSubmit() {
    if (!name.trim()) {
      error = 'Name is required';
      return;
    }

    if (!pin || pin.length !== 4) {
      error = 'PIN must be exactly 4 digits';
      return;
    }

    if (!/^\d{4}$/.test(pin)) {
      error = 'PIN must contain only numbers';
      return;
    }

    if (currentMode === 'create' && pin !== confirmPin) {
      error = 'PINs do not match';
      return;
    }

    loading = true;
    error = '';

    try {
      // Normalize name: trim and convert to lowercase for consistency
      const normalizedName = name.trim().toLowerCase();
      
      if (currentMode === 'create') {
        const parent = await choresStore.createParent({ name: normalizedName, pin });
        onParentCreated(parent);
      } else {
        const parent = await choresStore.verifyParent(normalizedName, pin);
        onParentVerified(parent);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSubmit();
    }
  }
</script>

<div class="parent-setup">
  <div class="flex items-center justify-between mb-6">
    <h2 class="text-xl font-semibold text-gray-900">
      {currentMode === 'create' ? 'Set Up Parent Account' : 'Parent Login'}
    </h2>
    <button
      on:click={onClose}
      class="text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Close"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <form on:submit|preventDefault={handleSubmit} class="space-y-4">
    <!-- Name Input -->
    <div>
      <label for="parent-name" class="block text-sm font-medium text-gray-700 mb-1">
        Parent Name
      </label>
      <input
        id="parent-name"
        type="text"
        bind:value={name}
        on:keydown={handleKeydown}
        placeholder="Enter your name"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        required
        disabled={loading}
      />
    </div>

    <!-- PIN Input -->
    <div>
      <label for="parent-pin" class="block text-sm font-medium text-gray-700 mb-1">
        4-Digit PIN
      </label>
      <input
        id="parent-pin"
        type="password"
        bind:value={pin}
        on:keydown={handleKeydown}
        placeholder="0000"
        maxlength="4"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-center text-lg tracking-widest"
        required
        disabled={loading}
      />
      <p class="text-xs text-gray-500 mt-1">
        Choose a 4-digit PIN for chore management
      </p>
    </div>

    <!-- Confirm PIN (only for create mode) -->
    {#if currentMode === 'create'}
      <div>
        <label for="confirm-pin" class="block text-sm font-medium text-gray-700 mb-1">
          Confirm PIN
        </label>
        <input
          id="confirm-pin"
          type="password"
          bind:value={confirmPin}
          on:keydown={handleKeydown}
          placeholder="0000"
          maxlength="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-center text-lg tracking-widest"
          required
          disabled={loading}
        />
      </div>
    {/if}

    <!-- Error Message -->
    {#if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-3">
        <div class="flex">
          <svg class="w-5 h-5 text-red-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-700">{error}</p>
        </div>
      </div>
    {/if}

    <!-- Submit Button -->
    <button
      type="submit"
      disabled={loading}
      class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {#if loading}
        <div class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {currentMode === 'create' ? 'Creating Account...' : 'Logging In...'}
        </div>
      {:else}
        {currentMode === 'create' ? 'Create Account' : 'Login'}
      {/if}
    </button>
  </form>

  <!-- Mode Switch -->
  <div class="mt-6 pt-4 border-t border-gray-200">
    <p class="text-center text-sm text-gray-600">
      {currentMode === 'create' ? 'Already have an account?' : "Don't have an account?"}
      <button
        on:click={() => switchMode(currentMode === 'create' ? 'login' : 'create')}
        class="ml-1 text-blue-600 hover:text-blue-700 font-medium"
        disabled={loading}
      >
        {currentMode === 'create' ? 'Login' : 'Create Account'}
      </button>
    </p>
  </div>

  <!-- Security Notice -->
  <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
    <div class="flex">
      <svg class="w-5 h-5 text-blue-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
      <div>
        <p class="text-sm text-blue-700 font-medium">Security Notice</p>
        <p class="text-xs text-blue-600 mt-1">
          Your PIN is securely hashed and stored. This system is for internal family use only.
        </p>
      </div>
    </div>
  </div>
</div>
