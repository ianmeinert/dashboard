<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from 'svelte';
  import SetDashboardLocationModal from './SetDashboardLocationModal.svelte';

  let city = '';
  let state = '';
  let zip = '';
  let country = 'US';
  let loading = false;
  let error = '';
  let current: any = null;
  let forecast: any[] = [];
  let lat: number | null = null;
  let lon: number | null = null;
  let preferredLocation: any = null;
  let pendingLocation: any = null;
  let showSetDefaultModal = false;
  let hasSearched = false;

  const dispatch = createEventDispatcher();

  export let dashboardLocation: any = null;

  async function fetchWeather(cityOverride?: string, stateOverride?: string) {
    loading = true;
    error = '';
    try {
      let locQuery = '';
      if (lat !== null && lon !== null) {
        locQuery = `lat=${lat}&lon=${lon}`;
      } else if (zip) {
        locQuery = `zip_code=${encodeURIComponent(zip)}`;
      } else if (cityOverride && stateOverride) {
        locQuery = `city=${encodeURIComponent(cityOverride)}&state=${encodeURIComponent(stateOverride)}`;
      } else {
        locQuery = `city=${encodeURIComponent(city)}&state=${encodeURIComponent(state)}`;
      }
      const currentUrl = `/api/weather/current?${locQuery}`;
      const forecastUrl = `/api/weather/forecast?${locQuery}`;
      console.debug('[Forecast] Fetching current:', currentUrl);
      let currentRes = await fetch(currentUrl);
      console.debug('[Forecast] Current response status:', currentRes.status);
      let forecastRes = await fetch(forecastUrl);
      console.debug('[Forecast] Fetching forecast:', forecastUrl);
      console.debug('[Forecast] Forecast response status:', forecastRes.status);
      if (!currentRes.ok || !forecastRes.ok) throw new Error('Weather API error');
      const currentData = await currentRes.json();
      const forecastData = await forecastRes.json();
      console.debug('[Forecast] Current data:', currentData);
      console.debug('[Forecast] Forecast data:', forecastData);
      current = currentData.weather;
      // Group forecast list by day
      const list = forecastData.forecast.list;
      const grouped: Record<string, any[]> = {};
      list.forEach((item: any) => {
        const date = item.dt_txt.split(' ')[0];
        if (!grouped[date]) grouped[date] = [];
        grouped[date].push(item);
      });
      // For each day, pick min/max temp and a representative icon/desc
      forecast = Object.entries(grouped).slice(0, 5).map(([date, items]: [string, any[]]) => {
        const temps = items.map(i => i.main.temp);
        const min = Math.min(...temps);
        const max = Math.max(...temps);
        // Use the icon/desc from the midday or first item
        const mid = items[Math.floor(items.length / 2)] || items[0];
        return {
          date,
          min,
          max,
          icon: mid.weather[0].icon,
          desc: mid.weather[0].description
        };
      });
    } catch (e: any) {
      error = e.message || 'Failed to fetch weather';
      console.debug('[Forecast] Error:', e);
    } finally {
      loading = false;
    }
  }

  function handleSubmit(e: Event) {
    e.preventDefault();
    // If all fields are blank, use geolocation
    if (!city && !state && !zip) {
      if (navigator.geolocation) {
        loading = true;
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            lat = pos.coords.latitude;
            lon = pos.coords.longitude;
            city = '';
            state = '';
            zip = '';
            fetchWeather();
            hasSearched = true;
          },
          (err) => {
            console.warn('Geolocation error:', err);
            useDefaultLocation();
          },
          { enableHighAccuracy: false, timeout: 5000 }
        );
      } else {
        useDefaultLocation();
      }
      return;
    }
    lat = null;
    lon = null;
    pendingLocation = {
      city: city || undefined,
      state: state || undefined,
      zip_code: zip || undefined,
      lat: lat !== null ? String(lat) : undefined,
      lon: lon !== null ? String(lon) : null
    };
    fetchWeatherWithLocation(pendingLocation);
    hasSearched = true;
  }

  function useDefaultLocation() {
    lat = null;
    lon = null;
    zip = '';
    // Do not update city/state input fields
    fetchWeather('Washington', 'DC');
  }

  async function fetchPreferredLocation() {
    try {
      const res = await fetch('/api/weather/settings');
      if (res.ok) {
        const data = await res.json();
        if (data.city || data.state || data.zip_code || data.lat || data.lon) {
          preferredLocation = data;
          city = data.city || '';
          state = data.state || '';
          zip = data.zip_code || '';
          lat = data.lat ? parseFloat(data.lat) : null;
          lon = data.lon ? parseFloat(data.lon) : null;
          await fetchWeather();
          return;
        }
      }
    } catch (e) {
      console.warn('Failed to fetch preferred location:', e);
    }
    // If not set, try geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          lat = pos.coords.latitude;
          lon = pos.coords.longitude;
          city = '';
          state = '';
          zip = '';
          fetchWeather();
        },
        (err) => {
          console.warn('Geolocation error:', err);
          useDefaultLocation();
        },
        { enableHighAccuracy: false, timeout: 5000 }
      );
    } else {
      useDefaultLocation();
    }
  }

  function cleanLocation(loc: any) {
    return {
      city: loc.city || undefined,
      state: loc.state || undefined,
      zip_code: loc.zip_code || undefined,
      lat: loc.lat != null ? String(loc.lat) : undefined,
      lon: loc.lon != null ? String(loc.lon) : undefined,
    };
  }

  async function setPreferredLocation(loc: any) {
    try {
      const payload = cleanLocation(loc);
      const res = await fetch('/api/weather/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const saved = await res.json();
        preferredLocation = saved;
        return saved;
      }
    } catch (e) {
      console.warn('Failed to set preferred location:', e);
    }
    return null;
  }

  async function fetchWeatherWithLocation(loc?: any) {
    if (loc) {
      city = loc.city || '';
      state = loc.state || '';
      zip = loc.zip_code || '';
      lat = loc.lat ? parseFloat(loc.lat) : null;
      lon = loc.lon ? parseFloat(loc.lon) : null;
    }
    await fetchWeather();
  }

  onMount(() => {
    if (dashboardLocation) {
      city = dashboardLocation.city || '';
      state = dashboardLocation.state || '';
      zip = dashboardLocation.zip_code || '';
      lat = dashboardLocation.lat ? parseFloat(dashboardLocation.lat) : null;
      lon = dashboardLocation.lon ? parseFloat(dashboardLocation.lon) : null;
      fetchWeather();
    } else {
      fetchPreferredLocation();
    }
  });

  onDestroy(() => {
    showSetDefaultModal = false;
  });

  // Confirm and set as preferred location
  async function confirmSetPreferred() {
    const saved = await setPreferredLocation(pendingLocation);
    if (saved) {
      // Fetch the canonical value from the backend
      await fetchPreferredLocation();
      console.debug('[Forecast] New preferred location from backend:', preferredLocation);
      dispatch('locationSet', preferredLocation);
    }
  }

  // Cancel confirmation, keep previous preferred location
  function cancelSetPreferred() {
    // Restore previous preferred location
    if (preferredLocation) {
      fetchWeatherWithLocation(preferredLocation);
    } else {
      fetchPreferredLocation();
    }
  }

  async function handleSetDefaultLocation() {
    showSetDefaultModal = false;
    await confirmSetPreferred();
    dispatch('defaultLocationSet');
    dispatch('close');
  }

  async function closeSetDefaultModal() {
    showSetDefaultModal = false;
    await cancelSetPreferred();
    await fetchPreferredLocation();
    dispatch('close');
  }

  function handleWidgetClose() {
    if (hasSearched) {
      showSetDefaultModal = true;
    } else {
      dispatch('close');
    }
  }

  export function requestClose() {
    handleWidgetClose();
  }
</script>

<div class="max-w-xl mx-auto relative" style="max-width: 700px;">
  <form class="mb-4" on:submit|preventDefault={handleSubmit}>
    <div class="search-bar flex w-full p-4 bg-white dark:bg-gray-900 rounded-lg shadow">
      <input
        class="flex-1 px-3 py-2 bg-transparent outline-none text-black dark:bg-gray-800 dark:text-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        placeholder="City"
        bind:value={city}
        disabled={!!zip}
        style="border: none;"
        title={zip ? 'Clear zip code to enter city/state' : ''}
      />
      <input
        class="w-24 px-3 py-2 bg-transparent outline-none text-black dark:bg-gray-800 dark:text-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        placeholder="State"
        maxlength="2"
        bind:value={state}
        disabled={!!zip}
        style="border: none;"
        title={zip ? 'Clear zip code to enter city/state' : ''}
      />
      <span class="text-gray-400 self-center px-2">or</span>
      <input
        class="zip-input px-3 py-2 bg-transparent outline-none text-black dark:bg-gray-800 dark:text-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        placeholder="Zip Code"
        bind:value={zip}
        maxlength="10"
        disabled={!!city || !!state}
        style="border: none; margin-right: 0.5rem; width: 6.5rem;"
        title={(city || state) ? 'Clear city/state to enter zip code' : ''}
      />
      <button type="submit" class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 transition-colors" style="border: none; border-radius: 0.75rem;">Search</button>
    </div>
  </form>

  {#if current}
    <div class="text-center text-gray-600 dark:text-gray-300 mb-2 text-lg font-medium">
      {#if current.name}
        {current.name}{state ? `, ${state}` : ''}
      {/if}
    </div>
  {/if}

  {#if loading}
    <div class="text-center text-gray-500 py-8">Loading weather…</div>
  {:else if error}
    <div class="text-center text-red-500 py-8">{error}</div>
  {:else if current}
    <div class="mb-6">
      <div class="flex items-center gap-4">
        <img src={`https://openweathermap.org/img/wn/${current.weather[0].icon}@2x.png`} alt={current.weather[0].description} class="w-16 h-16" />
        <div>
          <div class="text-3xl font-bold">{Math.round(current.main.temp)}°F</div>
          <div class="capitalize text-gray-600 dark:text-gray-300">{current.weather[0].description}</div>
        </div>
      </div>
      <div class="flex gap-6 mt-4 text-sm text-gray-600 dark:text-gray-300">
        <div>Wind: {current.wind.speed} mph</div>
        <div>Humidity: {current.main.humidity}%</div>
        <div>Feels like: {Math.round(current.main.feels_like)}°F</div>
      </div>
    </div>
    <div>
      <div class="font-semibold mb-2">5-Day Forecast</div>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
        {#each forecast as day}
          <div class="bg-gray-100 dark:bg-gray-800 rounded p-2 flex flex-col items-center">
            <div class="text-xs text-gray-500 mb-1">{new Date(day.date).toLocaleDateString(undefined, { weekday: 'short' })}</div>
            <img src={`https://openweathermap.org/img/wn/${day.icon}.png`} alt={day.desc} class="w-8 h-8" />
            <div class="text-xs capitalize text-gray-600 dark:text-gray-300 mb-1">{day.desc}</div>
            <div class="text-sm font-bold">{Math.round(day.max)}°</div>
            <div class="text-xs text-gray-500">{Math.round(day.min)}°</div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <SetDashboardLocationModal
    open={showSetDefaultModal}
    onConfirm={handleSetDefaultLocation}
    onCancel={closeSetDefaultModal}
    title="Set as dashboard location?"
    message="Do you want to set this location as your dashboard's default?"
  />
  <!-- TODO: Add geolocation, AQI, expand/collapse, better error handling -->
</div>

<style>
.search-bar {
  border: 1.5px solid #e5e7eb;
  border-radius: 0.75rem;
  background: #fff;
  /* overflow: hidden; */
}
.search-bar input {
  border: none;
  outline: none;
  background: transparent;
  padding: 0.75rem 1rem;
  font-size: 1rem;
}
.search-bar button {
  border: none;
  background: #2563eb;
  color: #fff;
  padding: 0 1.25rem;
  font-size: 1rem;
  border-radius: 0 0.75rem 0.75rem 0;
  cursor: pointer;
  transition: background 0.2s;
}
.search-bar button:hover {
  background: #1d4ed8;
}
.zip-input {
  min-width: 6.5rem;
  max-width: 8rem;
  margin-right: 0.5rem;
}
</style> 