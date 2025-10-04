<script context="module" lang="ts">
  // Types for consumers
  export interface CalendarEvent {
    id: string;
    summary: string;
    start: string;
    end: string;
    calendarId: string;
    calendarName: string;
    description: string;
    location: string;
    color_class?: string;
  }
</script>

<script lang="ts">
  // Generic, reusable calendar component
  import CalendarLegend from './CalendarLegend.svelte';
  import DayCell from './DayCell.svelte';
  import DayView from './DayView.svelte';
  import EventChip from './EventChip.svelte';
  import EventPopup from './EventPopup.svelte';

  export let events: CalendarEvent[] = [];
  export let calendarColors: Record<string, string> = {};
  export let calendarNames: Record<string, string> = {};
  export let loading: boolean = false;
  export let maxEventsPerCell: number = 3;

  // Optionally control the current month/year from parent
  export let initialYear: number = new Date().getFullYear();
  export let initialMonth: number = new Date().getMonth();

  // Event handlers (optional)
  export let onMonthChange: (year: number, month: number) => void = () => {};
  export let onEventClick: (event: CalendarEvent) => void = () => {};
  export let onDayClick: (date: string) => void = () => {};

  // Internal state
  let currentYear = initialYear;
  let currentMonth = initialMonth;
  let selectedEvent: CalendarEvent | null = null;
  let selectedDay: { day: number; month: number; year: number; isCurrent: boolean } | null = null;

  // Helpers
  function getDaysInMonth(year: number, month: number) {
    return new Date(year, month + 1, 0).getDate();
  }

  $: firstDayOfWeek = new Date(currentYear, currentMonth, 1).getDay();
  $: daysInMonth = getDaysInMonth(currentYear, currentMonth);
  $: daysInPrevMonth = getDaysInMonth(currentYear, currentMonth - 1 < 0 ? 11 : currentMonth - 1);
  $: leading = firstDayOfWeek;
  $: trailing = (7 - ((leading + daysInMonth) % 7)) % 7;

  // Build the full grid
  $: grid = [
    ...Array.from({ length: leading }, (_, i) => ({
      day: daysInPrevMonth - leading + i + 1,
      month: (currentMonth - 1 + 12) % 12,
      year: currentMonth === 0 ? currentYear - 1 : currentYear,
      isCurrent: false
    })),
    ...Array.from({ length: daysInMonth }, (_, i) => ({
      day: i + 1,
      month: currentMonth,
      year: currentYear,
      isCurrent: true
    })),
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
        return startDate <= dateStr && dateStr < endDate;
      }
      return startDate <= dateStr && dateStr <= endDate;
    });
  }

  function isAllDay(event: CalendarEvent): boolean {
    if (event.start.length === 10 && event.end.length === 10) {
      const start = new Date(event.start);
      const end = new Date(event.end);
      return (end.getTime() - start.getTime()) === 24 * 60 * 60 * 1000;
    }
    return false;
  }

  function isMultiDay(event: CalendarEvent): boolean {
    if (event.start.length === 10 && event.end.length === 10) {
      const start = new Date(event.start);
      const end = new Date(event.end);
      return (end.getTime() - start.getTime()) > 24 * 60 * 60 * 1000;
    }
    return event.start.slice(0, 10) !== event.end.slice(0, 10);
  }

  function getEventColorClass(event: CalendarEvent): string {
    const color = calendarColors[event.calendarId] || "bg-gray-200 text-gray-700";
    return color;
  }

  function cellDateStr(cell: { day: number; month: number; year: number; isCurrent: boolean }): string {
    const monthStr = String(cell.month + 1).padStart(2, '0');
    const dayStr = String(cell.day).padStart(2, '0');
    return `${cell.year}-${monthStr}-${dayStr}`;
  }

  function prevMonth() {
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
    } else {
      currentMonth--;
    }
    onMonthChange(currentYear, currentMonth);
  }

  function nextMonth() {
    if (currentMonth === 11) {
      currentMonth = 0;
      currentYear++;
    } else {
      currentMonth++;
    }
    onMonthChange(currentYear, currentMonth);
  }

  function openEvent(event: CalendarEvent) {
    selectedEvent = event;
  }

  function closeModal() {
    selectedEvent = null;
  }

  function openDayView(cell: { day: number; month: number; year: number; isCurrent: boolean }) {
    selectedDay = cell;
    onDayClick(cellDateStr(cell));
  }

  function closeDayView() {
    selectedDay = null;
    selectedEvent = null;
  }

  function openEventFromDayView(event: CustomEvent<CalendarEvent>) {
    selectedEvent = event.detail;
  }

  $: calendarIds = Array.from(new Set(events.map(e => e.calendarId)));
</script>

<div class="w-full sm:max-w-2xl mx-auto mt-8 dark:bg-gray-900 dark:text-white rounded-lg relative overflow-x-auto p-2">
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
          openOverflow={openDayView}
          openDayView={openDayView}
          maxEvents={maxEventsPerCell}
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
    {#if selectedDay}
      <div class="modal-backdrop"></div>
      <DayView
        date={cellDateStr(selectedDay)}
        events={eventsForCell(selectedDay)}
        {isAllDay}
        {isMultiDay}
        {getEventColorClass}
        formatTime={(dateStr) => {
          // Only show time for datetime formats, not date-only
          if (dateStr.length > 10) {
            return new Date(dateStr).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
          }
          return '';
        }}
        formatDate={(dateStr) => {
          // Handle both date-only ("2025-01-01") and datetime formats
          if (dateStr.length === 10) {
            // Date-only format
            const [year, month, day] = dateStr.split('-').map(Number);
            return new Date(year, month - 1, day).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          } else {
            // Datetime format
            return new Date(dateStr).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          }
        }}
        linkify={(text) => text ? text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline">$1</a>') : ''}
        on:close={closeDayView}
        on:openEvent={openEventFromDayView}
      />
    {/if}
    {#if selectedEvent}
      <div class="modal-backdrop" style="z-index: 60;"></div>
      <EventPopup
        event={selectedEvent}
        close={closeModal}
        {isAllDay}
        {isMultiDay}
        formatDate={(dateStr) => {
          // Handle both date-only ("2025-01-01") and datetime formats
          if (dateStr.length === 10) {
            // Date-only format
            const [year, month, day] = dateStr.split('-').map(Number);
            return new Date(year, month - 1, day).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          } else {
            // Datetime format
            return new Date(dateStr).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          }
        }}
        formatTime={(dateStr) => {
          // Only show time for datetime formats, not date-only
          if (dateStr.length > 10) {
            return new Date(dateStr).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
          }
          return '';
        }}
        {getEventColorClass}
        linkify={(text) => text ? text.replace(/(https?:\/\/[^\s]+)/g, '<a href=\"$1\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"text-blue-600 underline\">$1</a>') : ''}
        showCloseButton={true}
        dayEvents={selectedEvent ? eventsForCell({
          day: selectedEvent.start.length === 10 ?
            parseInt(selectedEvent.start.split('-')[2]) :
            new Date(selectedEvent.start).getDate(),
          month: selectedEvent.start.length === 10 ?
            parseInt(selectedEvent.start.split('-')[1]) - 1 :
            new Date(selectedEvent.start).getMonth(),
          year: selectedEvent.start.length === 10 ?
            parseInt(selectedEvent.start.split('-')[0]) :
            new Date(selectedEvent.start).getFullYear(),
          isCurrent: true
        }) : []}
      />
    {/if}
    <CalendarLegend
      calendarIds={calendarIds}
      {calendarColors}
      {calendarNames}
    />
  {/if}
</div>

<style>
  .modal-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(128,128,128,0.4);
    z-index: 40;
    pointer-events: auto;
    border-radius: 1rem;
  }
</style> 