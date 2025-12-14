// static/js/day_tasks.js — DAY TASK KANBAN — EXECUTION ONLY
document.addEventListener('DOMContentLoaded', () => {
  const kanban = document.getElementById('day-tasks-kanban');
  if (!kanban) return;

  const app = document.getElementById('calendar-app') || document.body;
  const year = app.dataset.year;
  const month = app.dataset.month.padStart(2, '0');
  const day = app.dataset.day.padStart(2, '0');

  const apiUrl = `/api/tasks/period/day/${year}/${month}/${day}`;

  fetch(apiUrl)
    .then(r => r.json())
    .then(tasks => {
      renderDayTasks(tasks);
      initDayTaskSortable(year, month, day);
    });
});

function renderDayTasks(tasks) {
  document.querySelectorAll('#day-tasks-kanban [id^="day-tasks-kanban-column-"]').forEach(col => col.innerHTML = '');

  tasks.forEach(task => {
    const column = document.getElementById(`day-tasks-kanban-column-${task.status}`);
    if (!column) return;

    const card = document.createElement('div');
    card.className = 'task-card bg-card p-5 rounded-xl shadow-lg border-l-4 cursor-pointer hover-grow';
    card.dataset.id = task.id;

    card.innerHTML = `
      <div class="font-bold text-white text-xl">${task.title}</div>
      <div class="text-sm text-muted mt-2">${task.priority}</div>
    `;

    card.addEventListener('click', () => openEditModal(task.id)); // reuse modal

    column.appendChild(card);
  });
}

function initDayTaskSortable(year, month, day) {
  document.querySelectorAll('#day-tasks-kanban [id^="day-tasks-kanban-column-"]').forEach(column => {
    if (column.sortable) column.sortable.destroy();

    column.sortable = new Sortable(column, {
      group: 'day-tasks',
      animation: 180,
      easing: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
      ghostClass: 'kanban-ghost',
      chosenClass: 'kanban-chosen',
      dragClass: 'kanban-dragging',
      cursor: 'grabbing',

      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;

        const taskId = evt.item.dataset.id;
        const newStatus = evt.to.id.replace('day-tasks-kanban-column-', '');

        fetch(`/api/tasks/${taskId}/move`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        })
        .then(() => {
          // Re-fetch day tasks
          const apiUrl = `/api/tasks/period/day/${year}/${month}/${day}`;
          fetch(apiUrl)
            .then(r => r.json())
            .then(tasks => renderDayTasks(tasks));
        });
      }
    });
  });
}