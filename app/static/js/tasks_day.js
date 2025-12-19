// static/js/tasks_day.js
// DAY PAGE TASK KANBAN — EXECUTION BATTLEFIELD
// Uses same modal, same card rendering, same drag engine — zero confusion
// Championship comments — future warriors will feel the power

console.log('tasks_day.js LOADED — DAILY EXECUTION MODE ARMED');

// SINGLE INITIALIZATION GUARD — NO DOUBLE-RUN IF LOADED TWICE
if (window.tasksDayInitialized) {
  console.log('tasks_day.js already running — skipping duplicate init');
} else {
  window.tasksDayInitialized = true;

  // NO TOP-LEVEL CONST APP — ELIMINATES REDECLARATION RISK FOREVER
  const calendarApp = document.getElementById('calendar-app') || document.body;

  // Safe guard: if no data attributes (wrong page), bail early
  if (!calendarApp.dataset.year || !calendarApp.dataset.month || !calendarApp.dataset.day) {
    console.warn('tasks_day.js: No calendar date data found — likely not on day view. Skipping.');
  } else {
    const year = calendarApp.dataset.year;
    const month = String(calendarApp.dataset.month).padStart(2, '0');
    const day = String(calendarApp.dataset.day).padStart(2, '0');
    const apiUrl = `/api/tasks/period/day/${year}/${month}/${day}`;

    function fetchDayTasks() {
      fetch(apiUrl)
        .then(r => {
          if (!r.ok) throw new Error('Fetch failed');
          return r.json();
        })
        .then(tasks => {
          console.log('DAY PAGE TASKS RAW DATA:', tasks);
          renderDayTasks(tasks);
        })
        .catch(err => {
          console.error('Failed to load day tasks:', err);
          // Still clear columns to avoid stale data
          document.querySelectorAll('#day-tasks-kanban [id^="day-tasks-kanban-column-"]').forEach(col => {
            col.innerHTML = '<p class="text-red-400 text-center py-8">Load failed — refresh page</p>';
          });
        });
    }

    function renderDayTasks(tasks) {
      // Clear all columns
      document.querySelectorAll('#day-tasks-kanban [id^="day-tasks-kanban-column-"]').forEach(col => {
        col.innerHTML = '<p class="text-gray-500 text-center py-8"></p>';
      });

      tasks.forEach(task => {
        const column = document.getElementById(`day-tasks-kanban-column-${task.status}`);
        if (!column) return;

        const card = createTaskCard(task);
        column.appendChild(card);
      });

      // Re-init drag after render
      initKanban('day-tasks-kanban', 'day-tasks', (taskId, newStatus) => {
        moveTask(taskId, newStatus, fetchDayTasks);
      });
    }

    // Shared card renderer — identical to global page
    function createTaskCard(task) {
      const card = document.createElement('div');
      card.className = 'task-card bg-card p-5 rounded-xl shadow-lg border-l-4 cursor-pointer hover-grow relative';
      card.classList.add(`border-${task.priority.toLowerCase()}-500`);
      card.dataset.id = task.id;

      card.innerHTML = `
        <div class="font-bold text-white text-xl">${escapeHtml(task.title)}</div>
        <div class="text-sm text-muted mt-2">${task.due_date || 'No due date'}</div>
        <div class="text-xs text-gray-500 mt-1">${task.tags || ''}</div>
      `;

      card.addEventListener('click', (e) => {
        if (e.target.closest('.btn-task-delete')) return;
        window.openEditModal(task);
      });

      return card;
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text || '';
      return div.innerHTML;
    }

    // Global refresh hook — used by modal delete/create
    window.refreshTasks = fetchDayTasks;

    // Kick it off
    document.addEventListener('DOMContentLoaded', fetchDayTasks);
  }
}