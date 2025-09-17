<script lang="ts">
import { onDestroy, onMount } from 'svelte';
import { serviceApi } from '../../utils/api.js';
import type { CalendarEvent } from './Calendar.svelte';
import Calendar from './Calendar.svelte';

// State
let events: CalendarEvent[] = [];
let calendarColors: Record<string, string> = {};
let calendarNames: Record<string, string> = {};
let loading = true;
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

// Cache keys
const CACHE_KEY = 'calendar_month_events';
const COLORS_CACHE_KEY = 'calendar_colors';
const CACHE_EXPIRY_KEY = 'calendar_cache_expiry';
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

let cacheExpiry: number | null = null;

function getMonthKey(year: number, month: number): string {
  return `${year}-${String(month + 1).padStart(2, '0')}`;
}

function getVisibleGridRange(year: number, month: number): { start: string; end: string } {
  const firstOfMonth = new Date(Date.UTC(year, month, 1, 0, 0, 0));
  const firstDayOfWeek = firstOfMonth.getUTCDay();
  const gridStart = new Date(firstOfMonth);
  gridStart.setUTCDate(gridStart.getUTCDate() - firstDayOfWeek);
  const gridEnd = new Date(gridStart);
  gridEnd.setUTCDate(gridEnd.getUTCDate() + 42);
  const start = gridStart.toISOString().slice(0, 10) + 'T00:00:00Z';
  const end = gridEnd.toISOString().slice(0, 10) + 'T00:00:00Z';
  return { start, end };
}

let monthEvents: Record<string, CalendarEvent[]> = {};

function loadFromCache() {
  if (typeof window === 'undefined') return;
  try {
    const expiry = localStorage.getItem(CACHE_EXPIRY_KEY);
    if (expiry && Date.now() > parseInt(expiry)) {
      clearCache();
      return;
    }
    const cachedEvents = localStorage.getItem(CACHE_KEY);
    if (cachedEvents) {
      monthEvents = JSON.parse(cachedEvents);
    }
    const cachedColors = localStorage.getItem(COLORS_CACHE_KEY);
    if (cachedColors) {
      calendarColors = JSON.parse(cachedColors);
    }
    // Ensure fallback colors are assigned for any calendars without colors
    assignFallbackColors();
  } catch (e) {
    clearCache();
  }
}

function saveToCache() {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(monthEvents));
    localStorage.setItem(COLORS_CACHE_KEY, JSON.stringify(calendarColors));
    localStorage.setItem(CACHE_EXPIRY_KEY, (Date.now() + CACHE_DURATION).toString());
  } catch (e) {}
}

function clearCache() {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(CACHE_KEY);
    localStorage.removeItem(COLORS_CACHE_KEY);
    localStorage.removeItem(CACHE_EXPIRY_KEY);
    monthEvents = {};
    calendarColors = {};
  } catch (e) {}
}

const fallbackColorPalette = [
  "bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-400",
  "bg-green-100 text-green-800 hover:bg-green-200 border-green-400",
  "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-400",
  "bg-red-100 text-red-800 hover:bg-red-200 border-red-400",
  "bg-purple-100 text-purple-800 hover:bg-purple-200 border-purple-400",
  "bg-pink-100 text-pink-800 hover:bg-pink-200 border-pink-400",
  "bg-indigo-100 text-indigo-800 hover:bg-indigo-200 border-indigo-400",
  "bg-teal-100 text-teal-800 hover:bg-teal-200 border-teal-400",
  "bg-orange-100 text-orange-800 hover:bg-orange-200 border-orange-400",
  "bg-cyan-100 text-cyan-800 hover:bg-cyan-200 border-cyan-400",
  "bg-lime-100 text-lime-800 hover:bg-lime-200 border-lime-400",
  "bg-rose-100 text-rose-800 hover:bg-rose-200 border-rose-400",
];

function assignFallbackColors() {
  const calendarIds = Array.from(new Set(events.map(e => e.calendarId)));
  console.log('Calendar IDs:', calendarIds);
  console.log('Current calendarColors:', calendarColors);
  calendarIds.forEach((id: string, idx: number) => {
    if (!calendarColors[id]) {
      calendarColors[id] = fallbackColorPalette[idx % fallbackColorPalette.length];
      console.log(`Assigning fallback color for calendar ${id}: ${calendarColors[id]}`);
    }
  });
  console.log('Final calendarColors:', calendarColors);
}

async function fetchMonthEvents(year: number, month: number) {
  const key = getMonthKey(year, month);
  if (monthEvents[key]) {
    return;
  }
  const { start, end } = getVisibleGridRange(year, month);
  loading = true;
  try {
    const response = await serviceApi.calendar.get(`/events?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
    const data = response.data;
    monthEvents[key] = data;
    saveToCache();
    if (year === currentYear && month === currentMonth) {
      events = data;
      loading = false;
    }
  } catch (e) {
    monthEvents[key] = [];
    saveToCache();
    if (year === currentYear && month === currentMonth) {
      events = [];
      loading = false;
    }
  }
}

function updateEventsForCurrentMonth() {
  const key = getMonthKey(currentYear, currentMonth);
  events = monthEvents[key] || [];
  loading = !monthEvents[key];
  // Update calendarNames and calendarColors
  calendarNames = {};
  // Don't reset calendarColors - preserve existing colors
  for (const event of events) {
    if (event.calendarId && event.calendarName) {
      calendarNames[event.calendarId] = event.calendarName;
    }
    if (event.calendarId && event.color_class) {
      calendarColors[event.calendarId] = event.color_class;
      console.log(`Setting color for calendar ${event.calendarId}: ${event.color_class}`);
    }
  }
  // Assign fallback colors for calendars without color_class
  assignFallbackColors();
}

function prevMonth() {
  if (currentMonth === 0) {
    currentMonth = 11;
    currentYear--;
  } else {
    currentMonth--;
  }
  updateEventsForCurrentMonth();
  if (!monthEvents[getMonthKey(currentYear, currentMonth)]) {
    loadVisibleAndAdjacentMonths();
  }
}

function nextMonth() {
  if (currentMonth === 11) {
    currentMonth = 0;
    currentYear++;
  } else {
    currentMonth++;
  }
  updateEventsForCurrentMonth();
  if (!monthEvents[getMonthKey(currentYear, currentMonth)]) {
    loadVisibleAndAdjacentMonths();
  }
}

async function loadVisibleAndAdjacentMonths() {
  await fetchMonthEvents(currentYear, currentMonth);
  let prevYear = currentMonth === 0 ? currentYear - 1 : currentYear;
  let prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
  fetchMonthEvents(prevYear, prevMonth);
  let nextYear = currentMonth === 11 ? currentYear + 1 : currentYear;
  let nextMonth = currentMonth === 11 ? 0 : currentMonth + 1;
  fetchMonthEvents(nextYear, nextMonth);
}

function isCacheStale(): boolean {
  if (typeof window === 'undefined') return true;
  if (cacheExpiry === null) {
    const expiryStr = localStorage.getItem(CACHE_EXPIRY_KEY);
    cacheExpiry = expiryStr ? parseInt(expiryStr) : null;
  }
  return !cacheExpiry || Date.now() > cacheExpiry;
}

function updateCacheExpiry() {
  if (typeof window === 'undefined') return;
  const expiryStr = localStorage.getItem(CACHE_EXPIRY_KEY);
  cacheExpiry = expiryStr ? parseInt(expiryStr) : null;
}

function refreshIfStale() {
  updateCacheExpiry();
  if (isCacheStale()) {
    // Force re-fetch for current month
    const key = getMonthKey(currentYear, currentMonth);
    delete monthEvents[key];
    fetchMonthEvents(currentYear, currentMonth).then(updateEventsForCurrentMonth);
  }
}

function ensureCurrentMonthData() {
  const key = getMonthKey(currentYear, currentMonth);
  const cached = monthEvents[key];
  if (!cached || (Array.isArray(cached) && cached.length === 0)) {
    delete monthEvents[key];
    fetchMonthEvents(currentYear, currentMonth).then(updateEventsForCurrentMonth);
  }
}

onMount(async () => {
  if (typeof window !== 'undefined') {
    loadFromCache();
    updateCacheExpiry();
    updateEventsForCurrentMonth();
    ensureCurrentMonthData();
    window.addEventListener('focus', () => {
      refreshIfStale();
      ensureCurrentMonthData();
    });
  }
  await loadVisibleAndAdjacentMonths();
});

// Clean up event listener on destroy
onDestroy(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('focus', () => {
      refreshIfStale();
      ensureCurrentMonthData();
    });
  }
});
</script>

<Calendar
  {events}
  {calendarColors}
  {calendarNames}
  {loading}
  initialYear={currentYear}
  initialMonth={currentMonth}
  onMonthChange={(year, month) => {
    currentYear = year;
    currentMonth = month;
    updateEventsForCurrentMonth();
    if (!monthEvents[getMonthKey(currentYear, currentMonth)]) {
      loadVisibleAndAdjacentMonths();
    }
  }}
/>

<!-- Debug info -->
{#if events.length > 0}
  <div class="mt-4 p-2 bg-gray-100 text-xs">
    <div>Events: {events.length}</div>
    <div>Calendar Colors: {JSON.stringify(calendarColors)}</div>
    <div>Calendar Names: {JSON.stringify(calendarNames)}</div>
  </div>
{/if} 