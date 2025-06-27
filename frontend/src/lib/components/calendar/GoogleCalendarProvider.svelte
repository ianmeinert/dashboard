<script lang="ts">
import { onMount } from 'svelte';
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
    if (cachedEvents) monthEvents = JSON.parse(cachedEvents);
    const cachedColors = localStorage.getItem(COLORS_CACHE_KEY);
    if (cachedColors) calendarColors = JSON.parse(cachedColors);
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

async function fetchCalendarColors() {
  try {
    const res = await fetch('http://localhost:8000/api/calendar/colors');
    const colors = await res.json();
    for (const [calendarId, colorInfo] of Object.entries(colors)) {
      calendarColors[calendarId] = (colorInfo as { color_class: string }).color_class;
    }
    saveToCache();
  } catch (e) {
    assignFallbackColors();
  }
}

function assignFallbackColors() {
  const calendarIds = Array.from(new Set(events.map(e => e.calendarId)));
  calendarIds.forEach((id: string, idx: number) => {
    if (!calendarColors[id]) {
      calendarColors[id] = fallbackColorPalette[idx % fallbackColorPalette.length];
    }
  });
}

async function fetchMonthEvents(year: number, month: number) {
  const key = getMonthKey(year, month);
  if (monthEvents[key]) return;
  const { start, end } = getVisibleGridRange(year, month);
  loading = true;
  try {
    const res = await fetch(`http://localhost:8000/api/calendar/events?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
    const data = await res.json();
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
  // Update calendarNames
  calendarNames = {};
  for (const event of events) {
    if (event.calendarId && event.calendarName) {
      calendarNames[event.calendarId] = event.calendarName;
    }
  }
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

onMount(async () => {
  if (typeof window !== 'undefined') {
    loadFromCache();
    updateEventsForCurrentMonth();
  }
  await fetchCalendarColors();
  await loadVisibleAndAdjacentMonths();
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