// static/js/calendar_events.js
// PHASE 8 — CALENDAR EVENTS DOMINATION — PURE PROTEIN
console.log('calendar_events.js LOADED — TIME GRID ARMED');

if (window.calendarEventsInitialized) {
  console.log('calendar_events.js already running — skipping');
} else {
  window.calendarEventsInitialized = true;

  const modal = document.getElementById('event-modal');
  const titleInput = document.getElementById('event-title');
  const startSelect = document.getElementById('event-start');
  const endSelect = document.getElementById('event-end');
  const saveBtn = document.getElementById('save-event-btn');
  const deleteBtn = document.getElementById('delete-event-btn');
  const closeBtn = document.getElementById('close-event-modal');

  const SLOTS = 38;
  const START_HOUR = 5;

  function generateTimeOptions() {
    const options = [];
    for (let slot = 0; slot < SLOTS; slot++) {
      const hour = START_HOUR + Math.floor(slot / 2);
      const minute = (slot % 2) * 30;
      const hour12 = ((hour - 1) % 12) + 1;
      const ampm = hour < 12 ? 'AM' : 'PM';
      const label = `${hour12}:${minute.toString().padStart(2,'0')} ${ampm}`;
      const value = slot;
      options.push({label, value});
    }
    return options;
  }

  const timeOptions = generateTimeOptions();

  function populateSelects(selectedStart = 0, selectedEnd = 2) { // default 30 min
    [startSelect, endSelect].forEach(select => {
      select.innerHTML = '';
      timeOptions.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.label;
        if (select === startSelect && opt.value == selectedStart) option.selected = true;
        if (select === endSelect && opt.value == selectedEnd) option.selected = true;
        select.appendChild(option);
      });
    });
  }

  function openModal(slotIndex = null, event = null) {
    document.getElementById('event-id').value = event?.id || '';
    titleInput.value = event?.title || '';
    deleteBtn.classList.toggle('hidden', !event);

    if (event) {
      // Existing event — calculate slots
      const startSlot = timeToSlot(event.start_datetime);
      const endSlot = timeToSlot(event.end_datetime);
      populateSelects(startSlot, endSlot);
    } else {
      // New from slot click
      const startSlot = slotIndex;
      const endSlot = Math.min(slotIndex + 2, SLOTS - 1); // 30 min default
      populateSelects(startSlot, endSlot);
    }

    modal.classList.remove('invisible', 'opacity-0');
    modal.classList.add('visible', 'opacity-100');
  }

  function closeModal() {
    modal.classList.add('invisible', 'opacity-0');
    modal.classList.remove('visible', 'opacity-100');
  }

  function slotToTime(slot) {
    const hour = START_HOUR + Math.floor(slot / 2);
    const minute = (slot % 2) * 30;
    return `${hour.toString().padStart(2,'0')}:${minute.toString().padStart(2,'0')}:00`;
  }

  function timeToSlot(dtStr) {
    const dt = new Date(dtStr);
    const hour = dt.getHours();
    const minute = dt.getMinutes();
    return (hour - START_HOUR) * 2 + (minute >= 30 ? 1 : 0);
  }

  function getCurrentDay() {
    const app = document.getElementById('calendar-app');
    return `${app.dataset.year}-${String(app.dataset.month).padStart(2,'0')}-${String(app.dataset.day).padStart(2,'0')}`;
  }

  function fetchAndRenderEvents() {
    const dayStr = getCurrentDay(); // "2025-12-15"
    const [year, month, day] = dayStr.split('-');
    const url = `/api/events/day/${year}/${month}/${day}`;
    
    fetch(url)
        .then(r => r.json())
        .then(events => renderEvents(events))
        .catch(err => console.error('Event load failed:', err));
  }

function renderEvents(events) {
  document.querySelectorAll('.event-container').forEach(c => c.innerHTML = '');

  const groups = {};
  events.forEach(ev => {
    const startSlot = timeToSlot(ev.start_datetime);
    if (!groups[startSlot]) groups[startSlot] = [];
    groups[startSlot].push(ev);
  });

  Object.keys(groups).forEach(slotStr => {
    const slot = parseInt(slotStr);
    let group = groups[slot];

    // Calculate duration for each
    group.forEach(ev => {
      ev.durationSlots = Math.max(1, timeToSlot(ev.end_datetime) - slot);
    });

    // Find longest
    const maxDuration = Math.max(...group.map(ev => ev.durationSlots));
    const hasLong = maxDuration > 1;

    // Sort: long events first, then by ID descending (newest last)
    group.sort((a, b) => {
      if (a.durationSlots === maxDuration && b.durationSlots !== maxDuration) return -1;
      if (b.durationSlots === maxDuration && a.durationSlots !== maxDuration) return 1;
      return b.id - a.id; // newest last
    });

    const container = document.querySelector(`[data-slot="${slot}"] .event-container`);
    if (!container) return;

    const count = group.length;

    group.forEach((ev, index) => {
      const block = document.createElement('div');
      let classes = `event-block ${ev.source === 'outlook_ics' ? 'imported-event' : 'manual-event'}`;
      if (hasLong && ev.durationSlots === maxDuration) classes += ' long-event';
      classes += ` overlap-${count}`;
      block.className = classes;
      block.dataset.id = ev.id;

      block.style.height = `calc(${ev.durationSlots * 100}% - 8px)`;
      block.style.top = '4px';

      const titleText = ev.title.length > 35 ? ev.title.substring(0, 32) + '...' : ev.title;
      block.innerHTML = `
        <div class="text-xl font-black truncate px-3 py-2 leading-tight">${titleText}</div>
      `;

      block.addEventListener('click', (e) => {
        e.stopPropagation();
        openModal(null, ev);
      });

      container.appendChild(block);
    });
  });
}

  // DELEGATED SLOT CLICK
  document.querySelector('.grid-rows-38').addEventListener('click', (e) => {
    const slotDiv = e.target.closest('[data-slot]');
    if (!slotDiv) return;
    const slotIndex = parseInt(slotDiv.dataset.slot);
    openModal(slotIndex);
  });

  saveBtn.onclick = () => {
    const id = document.getElementById('event-id').value;
    const dayStr = getCurrentDay(); // "2025-12-15"
    const [year, month, day] = dayStr.split('-');
    const payload = {
        title: titleInput.value.trim(),
        start_time: slotToTime(parseInt(startSelect.value)),
        end_time: slotToTime(parseInt(endSelect.value)),
        year: parseInt(year),
        month: parseInt(month),
        day: parseInt(day)
    };

    const method = id ? 'PATCH' : 'POST';
    const url = id ? `/api/events/${id}` : '/api/events';

    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(r => {
      if (!r.ok) throw new Error('Save failed');
      closeModal();
      fetchAndRenderEvents();
    })
    .catch(err => console.error(err));
  };

  deleteBtn.onclick = () => {
    if (!confirm('Delete this event forever?')) return;
    const id = document.getElementById('event-id').value;
    fetch(`/api/events/${id}`, { method: 'DELETE' })
      .then(() => {
        closeModal();
        fetchAndRenderEvents();
      });
  };

  closeBtn.onclick = modal.onclick = (e) => {
    if (e.target === modal || e.target === closeBtn) closeModal();
  };

  // Initial load
  document.addEventListener('DOMContentLoaded', () => {
    populateSelects();
    fetchAndRenderEvents();
  });

  // Expose for future use
  window.refreshCalendarEvents = fetchAndRenderEvents;
}

// DAILY TIME GRID COLLAPSE DOMINATION — CONSISTENT WITH GOAL TREE
function setupCalendarCollapse() {
  const header = document.getElementById('calendar-toggle-header');
  const collapsed = document.getElementById('calendar-grid-collapsed');
  const expanded = document.getElementById('calendar-grid-expanded');
  const icon = document.getElementById('calendar-toggle-icon');

  if (!header || !collapsed || !expanded || !icon) return;

  // Restore saved state (default: open)
  const saved = localStorage.getItem('day-calendar-open');
  const isOpen = saved === null || saved === 'true'; // default true = expanded

    function setOpen(open) {
    if (open) {
      expanded.classList.remove('hidden');
      icon.textContent = '▼';
      header.classList.remove('rounded-xl');     // Make bottom corners square when open
      header.classList.add('rounded-t-xl');
    } else {
      expanded.classList.add('hidden');
      icon.textContent = '▶';
      header.classList.remove('rounded-t-xl');
      header.classList.add('rounded-xl');        // Full rounded when collapsed
    }
    localStorage.setItem('day-calendar-open', open);
  }

  setOpen(isOpen);

  // Toggle on click
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-action="toggle-calendar"]')) {
      setOpen(expanded.classList.contains('hidden'));
    }
  });
}

// Run after DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // ... existing code ...
  setupCalendarCollapse();
});