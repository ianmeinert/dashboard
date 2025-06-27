<script lang="ts">
  import { onDestroy, onMount } from 'svelte';

  let systemStatus: any = null;
  let metrics: any = null;
  let recentLogs: any = null;
  let loading = true;
  let error: string | null = null;
  let refreshInterval: number;

  // Auto-refresh every 30 seconds
  const REFRESH_INTERVAL = 30000;

  async function fetchSystemStatus() {
    try {
      const response = await fetch('http://localhost:8000/api/monitoring/status');
      if (!response.ok) throw new Error('Failed to fetch system status');
      systemStatus = await response.json();
    } catch (e) {
      error = `Failed to fetch system status: ${e}`;
    }
  }

  async function fetchMetrics() {
    try {
      const response = await fetch('http://localhost:8000/api/monitoring/metrics?hours=1');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      metrics = await response.json();
    } catch (e) {
      console.error('Failed to fetch metrics:', e);
    }
  }

  async function fetchRecentLogs() {
    try {
      const response = await fetch('http://localhost:8000/api/monitoring/logs?lines=20');
      if (!response.ok) throw new Error('Failed to fetch logs');
      recentLogs = await response.json();
    } catch (e) {
      console.error('Failed to fetch logs:', e);
    }
  }

  async function refreshAll() {
    loading = true;
    error = null;
    
    await Promise.all([
      fetchSystemStatus(),
      fetchMetrics(),
      fetchRecentLogs()
    ]);
    
    loading = false;
  }

  function getStatusColor(status: string): string {
    switch (status) {
      case 'operational':
      case 'healthy':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      case 'degraded':
      case 'unhealthy':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      default:
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
    }
  }

  function formatResponseTime(time: number): string {
    if (time < 1) return `${(time * 1000).toFixed(0)}ms`;
    return `${time.toFixed(2)}s`;
  }

  function formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  onMount(() => {
    refreshAll();
    refreshInterval = setInterval(refreshAll, REFRESH_INTERVAL);
  });

  onDestroy(() => {
    if (refreshInterval) clearInterval(refreshInterval);
  });
</script>

<div class="max-w-6xl mx-auto p-6 space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">System Monitoring</h1>
    <button
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      on:click={refreshAll}
      disabled={loading}
    >
      {loading ? 'Refreshing...' : 'Refresh'}
    </button>
  </div>

  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded dark:bg-red-900 dark:text-red-200">
      {error}
    </div>
  {/if}

  {#if systemStatus}
    <!-- System Status Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Overall Status -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Status</h2>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">Overall:</span>
            <span class={`px-2 py-1 rounded-full text-sm font-medium ${getStatusColor(systemStatus.status)}`}>
              {systemStatus.status}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">Database:</span>
            <span class={`px-2 py-1 rounded-full text-sm font-medium ${getStatusColor(systemStatus.health.checks.database ? 'healthy' : 'unhealthy')}`}>
              {systemStatus.health.checks.database ? 'Healthy' : 'Unhealthy'}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">Google Calendar:</span>
            <span class={`px-2 py-1 rounded-full text-sm font-medium ${getStatusColor(systemStatus.health.checks.google_calendar ? 'healthy' : 'unhealthy')}`}>
              {systemStatus.health.checks.google_calendar ? 'Healthy' : 'Unhealthy'}
            </span>
          </div>
        </div>
      </div>

      <!-- Performance Metrics -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Performance (Last Hour)</h2>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">API Calls:</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {systemStatus.performance.api_calls_last_hour}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">Avg Response:</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {formatResponseTime(systemStatus.performance.avg_response_time)}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600 dark:text-gray-300">Errors:</span>
            <span class="font-medium text-gray-900 dark:text-white">
              {systemStatus.performance.errors_last_hour}
            </span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div class="space-y-2">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            class="block w-full px-4 py-2 bg-blue-600 text-white text-center rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            API Documentation
          </a>
          <a
            href="http://localhost:8000/api/monitoring/health"
            target="_blank"
            class="block w-full px-4 py-2 bg-green-600 text-white text-center rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Health Check
          </a>
        </div>
      </div>
    </div>
  {/if}

  {#if metrics}
    <!-- Detailed Metrics -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Detailed Metrics (Last Hour)</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {metrics.metrics.total_api_calls}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Total API Calls</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600 dark:text-green-400">
            {formatResponseTime(metrics.metrics.avg_response_time)}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Avg Response Time</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-red-600 dark:text-red-400">
            {metrics.metrics.api_errors}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">API Errors</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {metrics.metrics.total_errors}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-300">Total Errors</div>
        </div>
      </div>
    </div>
  {/if}

  {#if recentLogs}
    <!-- Recent Logs -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Logs</h2>
      <div class="bg-gray-100 dark:bg-gray-900 rounded p-4 max-h-64 overflow-y-auto">
        {#each recentLogs.logs as log}
          <div class="text-sm font-mono text-gray-800 dark:text-gray-200 mb-1">
            {log}
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Auto-refresh indicator -->
  <div class="text-center text-sm text-gray-500 dark:text-gray-400">
    Auto-refreshing every {REFRESH_INTERVAL / 1000} seconds
  </div>
</div> 