<script lang="ts">
  // Type for multi-day bar
  type MultiDayBar = { event: CalendarEvent; firstIdx: number; span: number };

  import { onMount } from 'svelte';
  import CalendarLegend from './CalendarLegend.svelte';
  import DayCell from './DayCell.svelte';
  import DayView from './DayView.svelte';
  import EventChip from './EventChip.svelte';
  import EventPopup from './EventPopup.svelte';

  function getDaysInMonth(year: number, month: number) {
    return new Date(year, month + 1, 0).getDate();
  }

  const today = new Date();
  let currentYear = today.getFullYear();
  let currentMonth = today.getMonth();

  // Define a type for calendar events
  interface CalendarEvent {
    id: string;
    summary: string;
    start: string;
    end: string;
    calendarId: string;
    calendarName: string;
    description: string;
    location: string;
  }

  let monthEvents: Record<string, CalendarEvent[]> = {};
  let events: CalendarEvent[] = [];
  let selectedEvent: CalendarEvent | null = null;
  let selectedDay: { day: number; month: number; year: number; isCurrent: boolean } | null = null;
  let loading = true;
  let calendarColors: Record<string, string> = {};

  // Cache keys for localStorage
  const CACHE_KEY = 'calendar_month_events';
  const COLORS_CACHE_KEY = 'calendar_colors';
  const CACHE_EXPIRY_KEY = 'calendar_cache_expiry';
  const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

  // Load cached data from localStorage
  function loadFromCache() {
    if (typeof window === 'undefined') return; // Skip if not in browser
    
    try {
      // Check if cache is expired
      const expiry = localStorage.getItem(CACHE_EXPIRY_KEY);
      if (expiry && Date.now() > parseInt(expiry)) {
        // Cache expired, clear it
        clearCache();
        return;
      }

      // Load month events
      const cachedEvents = localStorage.getItem(CACHE_KEY);
      if (cachedEvents) {
        monthEvents = JSON.parse(cachedEvents);
      }

      // Load calendar colors
      const cachedColors = localStorage.getItem(COLORS_CACHE_KEY);
      if (cachedColors) {
        calendarColors = JSON.parse(cachedColors);
      }
    } catch (e) {
      console.error('Failed to load from cache:', e);
      clearCache();
    }
  }

  // Save data to localStorage
  function saveToCache() {
    if (typeof window === 'undefined') return; // Skip if not in browser
    
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(monthEvents));
      localStorage.setItem(COLORS_CACHE_KEY, JSON.stringify(calendarColors));
      localStorage.setItem(CACHE_EXPIRY_KEY, (Date.now() + CACHE_DURATION).toString());
    } catch (e) {
      console.error('Failed to save to cache:', e);
    }
  }

  // Clear cache
  function clearCache() {
    if (typeof window === 'undefined') return; // Skip if not in browser
    
    try {
      localStorage.removeItem(CACHE_KEY);
      localStorage.removeItem(COLORS_CACHE_KEY);
      localStorage.removeItem(CACHE_EXPIRY_KEY);
      monthEvents = {};
      calendarColors = {};
    } catch (e) {
      console.error('Failed to clear cache:', e);
    }
  }

  // Fallback color palette for calendars without assigned colors
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
      // Convert the backend color data to the format expected by the frontend
      for (const [calendarId, colorInfo] of Object.entries(colors)) {
        calendarColors[calendarId] = (colorInfo as { color_class: string }).color_class;
      }
      saveToCache(); // Save colors to localStorage
    } catch (e) {
      console.error('Failed to fetch calendar colors:', e);
      // Fall back to dynamic assignment if colors can't be fetched
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

  function getEventColorClass(event: CalendarEvent): string {
    return calendarColors[event.calendarId] || "bg-gray-200 text-gray-700";
  }

  function getMonthKey(year: number, month: number): string {
    return `${year}-${String(month + 1).padStart(2, '0')}`;
  }

  function getMonthRange(year: number, month: number): { start: string; end: string } {
    const start = new Date(Date.UTC(year, month, 1, 0, 0, 0));
    const end = new Date(Date.UTC(year, month + 1, 1, 0, 0, 0));
    return {
      start: start.toISOString().slice(0, 10) + 'T00:00:00Z',
      end: end.toISOString().slice(0, 10) + 'T00:00:00Z',
    };
  }

  // Calculate the full visible date range for the current grid (including leading/trailing days)
  function getVisibleGridRange(year: number, month: number): { start: string; end: string } {
    // Calculate the first day of the month
    const firstOfMonth = new Date(Date.UTC(year, month, 1, 0, 0, 0));
    // What day of the week does the first fall on?
    const firstDayOfWeek = firstOfMonth.getUTCDay(); // 0=Sun, 1=Mon, ...
    // The grid always starts on Sunday, so subtract days to get to the previous Sunday
    const gridStart = new Date(firstOfMonth);
    gridStart.setUTCDate(gridStart.getUTCDate() - firstDayOfWeek);
    // The grid always has 6 rows of 7 days = 42 days
    const gridEnd = new Date(gridStart);
    gridEnd.setUTCDate(gridEnd.getUTCDate() + 42); // exclusive
    // Format as ISO 8601
    const start = gridStart.toISOString().slice(0, 10) + 'T00:00:00Z';
    const end = gridEnd.toISOString().slice(0, 10) + 'T00:00:00Z';
    return { start, end };
  }

  async function fetchMonthEvents(year: number, month: number) {
    const key = getMonthKey(year, month);
    if (monthEvents[key]) return; // Already loaded
    // Use the full visible grid range for the API call
    const { start, end } = getVisibleGridRange(year, month);
    loading = true;
    try {
      const res = await fetch(`http://localhost:8000/api/calendar/events?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
      const data = await res.json();
      monthEvents[key] = data;
      saveToCache(); // Save to localStorage after fetching
      // If this is the currently viewed month, update events
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

  async function loadVisibleAndAdjacentMonths() {
    // Current
    await fetchMonthEvents(currentYear, currentMonth);
    // Previous
    let prevYear = currentMonth === 0 ? currentYear - 1 : currentYear;
    let prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    fetchMonthEvents(prevYear, prevMonth);
    // Next
    let nextYear = currentMonth === 11 ? currentYear + 1 : currentYear;
    let nextMonth = currentMonth === 11 ? 0 : currentMonth + 1;
    fetchMonthEvents(nextYear, nextMonth);
  }

  function updateEventsForCurrentMonth() {
    const key = getMonthKey(currentYear, currentMonth);
    events = monthEvents[key] || [];
    loading = !monthEvents[key];
  }

  function prevMonth() {
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
    } else {
      currentMonth--;
    }
    trackUsageEvent('month_navigation', {
      direction: 'previous',
      new_month: currentMonth,
      new_year: currentYear
    });
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
    trackUsageEvent('month_navigation', {
      direction: 'next',
      new_month: currentMonth,
      new_year: currentYear
    });
    updateEventsForCurrentMonth();
    if (!monthEvents[getMonthKey(currentYear, currentMonth)]) {
      loadVisibleAndAdjacentMonths();
    }
  }

  onMount(async () => {
    if (typeof window !== 'undefined') {
      loadFromCache();
      updateEventsForCurrentMonth();
    }
    await fetchCalendarColors();
    await loadVisibleAndAdjacentMonths();
  });

  // Calculate all cells for a 6-row grid (42 cells)
  $: firstDayOfWeek = new Date(currentYear, currentMonth, 1).getDay();
  $: daysInMonth = getDaysInMonth(currentYear, currentMonth);
  $: daysInPrevMonth = getDaysInMonth(currentYear, currentMonth - 1 < 0 ? 11 : currentMonth - 1);
  $: leading = firstDayOfWeek;
  $: trailing = 42 - (leading + daysInMonth);

  // Build the full grid
  $: grid = [
    // Leading days (previous month)
    ...Array.from({ length: leading }, (_, i) => ({
      day: daysInPrevMonth - leading + i + 1,
      month: (currentMonth - 1 + 12) % 12,
      year: currentMonth === 0 ? currentYear - 1 : currentYear,
      isCurrent: false
    })),
    // Current month days
    ...Array.from({ length: daysInMonth }, (_, i) => ({
      day: i + 1,
      month: currentMonth,
      year: currentYear,
      isCurrent: true
    })),
    // Trailing days (next month)
    ...Array.from({ length: trailing }, (_, i) => ({
      day: i + 1,
      month: (currentMonth + 1) % 12,
      year: currentMonth === 11 ? currentYear + 1 : currentYear,
      isCurrent: false
    }))
  ];

  function isTodayCell(cell: { day: number; month: number; year: number; isCurrent: boolean }): boolean {
    const t = new Date();
    return cell.day === t.getDate() && cell.month === t.getMonth() && cell.year === t.getFullYear();
  }

  function eventsForCell(cell: { day: number; month: number; year: number; isCurrent: boolean }): CalendarEvent[] {
    const monthStr = String(cell.month + 1).padStart(2, '0');
    const dayStr = String(cell.day).padStart(2, '0');
    const dateStr = `${cell.year}-${monthStr}-${dayStr}`;
    return events.filter((e: CalendarEvent) => {
      const startDate = e.start.slice(0, 10);
      const endDate = e.end.slice(0, 10);
      if (isAllDay(e)) {
        // Use exclusive end date logic for all-day events
        return startDate <= dateStr && dateStr < endDate;
      }
      // For timed events, include if the event occurs on this date
      return startDate <= dateStr && dateStr <= endDate;
    });
  }

  // Helper to auto-link URLs in description
  function linkify(text: string): string {
    if (!text) return '';
    return text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline">$1</a>');
  }

  // Usage tracking functions
  async function trackUsageEvent(eventType: string, details?: any) {
    try {
      await fetch('http://localhost:8000/api/monitoring/usage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: eventType,
          details: details
        })
      });
    } catch (e) {
      console.error('Failed to track usage event:', e);
    }
  }

  function openEvent(event: CalendarEvent) {
    selectedEvent = event;
    trackUsageEvent('event_clicked', {
      event_id: event.id,
      event_summary: event.summary,
      calendar_name: event.calendarName
    });
  }

  function closeModal() {
    selectedEvent = null;
  }

  $: calendarNames = {} as Record<string, string>;
  $: {
    for (const event of events as CalendarEvent[]) {
      const ev: CalendarEvent = event;
      if (ev.calendarId && ev.calendarName) {
        calendarNames[ev.calendarId] = ev.calendarName;
      }
    }
  }

  $: calendarIds = Array.from(new Set(events.map(e => e.calendarId)));
  $: {
    // Update colors when new calendars are discovered
    calendarIds.forEach((id: string) => {
      if (!calendarColors[id]) {
        // Assign fallback color for new calendars
        const idx = Object.keys(calendarColors).length;
        calendarColors[id] = fallbackColorPalette[idx % fallbackColorPalette.length];
      }
    });
  }

  // Helper: get date string for a cell
  function cellDateStr(cell: { day: number; month: number; year: number; isCurrent: boolean }): string {
    const monthStr = String(cell.month + 1).padStart(2, '0');
    const dayStr = String(cell.day).padStart(2, '0');
    return `${cell.year}-${monthStr}-${dayStr}`;
  }

  // Helper: get week index for a cell
  function getWeekIndex(cellIdx: number): number {
    return Math.floor(cellIdx / 7);
  }

  function isAllDay(event: CalendarEvent): boolean {
    // All-day if both start and end are date-only strings and end is exactly one day after start
    if (event.start.length === 10 && event.end.length === 10) {
      const start = new Date(event.start);
      const end = new Date(event.end);
      return (end.getTime() - start.getTime()) === 24 * 60 * 60 * 1000;
    }
    return false;
  }

  function isMultiDay(event: CalendarEvent): boolean {
    // Multi-day all-day if both are date-only and end is more than one day after start
    if (event.start.length === 10 && event.end.length === 10) {
      const start = new Date(event.start);
      const end = new Date(event.end);
      return (end.getTime() - start.getTime()) > 24 * 60 * 60 * 1000;
    }
    // Or if start and end datetimes are on different days
    return event.start.slice(0, 10) !== event.end.slice(0, 10);
  }

  // Helper to format a date string as 'Wednesday, June 25, 2025'
  function formatDate(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  }

  // Helper to format a time string as '5:30 PM'
  function formatTime(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  }

  const MAX_EVENTS_PER_CELL = 3;
  let overflowEvents: CalendarEvent[] = [];
  let overflowCellDate: string | undefined = undefined;
  function openOverflow(cell: { day: number; month: number; year: number; isCurrent: boolean }) {
    // Instead of opening OverflowPopup, open DayView for the selected day
    selectedDay = cell;
    trackUsageEvent('overflow_clicked', {
      date: cellDateStr(cell),
      event_count: eventsForCell(cell).length
    });
  }
  function closeOverflow() {
    overflowEvents = [];
    overflowCellDate = undefined;
  }

  function openDayView(cell: { day: number; month: number; year: number; isCurrent: boolean }) {
    selectedDay = cell;
    trackUsageEvent('day_clicked', {
      date: cellDateStr(cell),
      is_current_month: cell.isCurrent
    });
  }

  function closeDayView() {
    selectedDay = null;
  }

  function openEventFromDayView(event: CustomEvent<CalendarEvent>) {
    selectedEvent = event.detail;
    selectedDay = null; // Close day view when opening event
  }
</script>

<div class="max-w-2xl mx-auto mt-8 dark:bg-gray-900 dark:text-white rounded-lg">
  {#if loading}
    <div class="text-center py-8 text-gray-500 dark:text-gray-300">Loading events…</div>
  {:else}
    <div class="flex justify-between items-center mb-4 select-none">
      <button
        class="px-4 py-2 bg-gray-200 dark:bg-gray-800 dark:text-white rounded-lg text-2xl font-bold shadow active:bg-gray-300 dark:active:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        style="min-width:44px; min-height:44px;"
        aria-label="Previous month"
        on:click={prevMonth}
      >&lt;</button>
      <h2 class="text-2xl font-bold px-4 select-none">
        {new Date(currentYear, currentMonth).toLocaleString('default', { month: 'long' })} {currentYear}
      </h2>
      <button
        class="px-4 py-2 bg-gray-200 dark:bg-gray-800 dark:text-white rounded-lg text-2xl font-bold shadow active:bg-gray-300 dark:active:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        style="min-width:44px; min-height:44px;"
        aria-label="Next month"
        on:click={nextMonth}
      >&gt;</button>
    </div>
    <div class="grid grid-cols-7 gap-1 text-center font-semibold select-none">
      {#each ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'] as d}
        <div class="dark:text-gray-300">{d}</div>
      {/each}
    </div>
    <div class="grid grid-cols-7 gap-1 mt-1">
      {#each grid as cell (cell.year + '-' + cell.month + '-' + cell.day)}
        <DayCell
          {cell}
          events={eventsForCell(cell)}
          isToday={isTodayCell(cell)}
          openEvent={openEvent}
          openOverflow={openOverflow}
          openDayView={openDayView}
          maxEvents={MAX_EVENTS_PER_CELL}
        >
          <svelte:fragment slot="event" let:event>
            <EventChip
              {event}
              {openEvent}
              {isAllDay}
              {isMultiDay}
              {getEventColorClass}
            />
          </svelte:fragment>
        </DayCell>
      {/each}
    </div>
    {#if selectedEvent}
      <EventPopup
        event={selectedEvent}
        close={closeModal}
        {isAllDay}
        {isMultiDay}
        {formatDate}
        {formatTime}
        {getEventColorClass}
        {linkify}
        showCloseButton={true}
        dayEvents={eventsForCell({
          day: new Date(selectedEvent.start).getDate(),
          month: new Date(selectedEvent.start).getMonth(),
          year: new Date(selectedEvent.start).getFullYear(),
          isCurrent: true
        })}
      />
    {/if}
    {#if selectedDay}
      <DayView
        date={cellDateStr(selectedDay)}
        events={eventsForCell(selectedDay)}
        {isAllDay}
        {isMultiDay}
        {getEventColorClass}
        {formatTime}
        {formatDate}
        {linkify}
        on:close={closeDayView}
        on:openEvent={openEventFromDayView}
      />
    {/if}
    <CalendarLegend
      {calendarIds}
      {calendarColors}
      {calendarNames}
    />
  {/if}
</div> 