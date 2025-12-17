// static/js/tasks_global.js
// TASKS PAGE — FULL DOMINATION CENTER
// Replaces old tasks_kanban.js — now uses shared core + modal

console.log('tasks_global.js LOADED — FULL TASK EMPIRE ONLINE');

let allTasks = [];

function fetchAllTasks() {
  fetch('/api/tasks')
    .then(r => r.json())
    .then(tasks => {
      allTasks = tasks;
      renderTasks();
    });
}

function renderTasks() {
  document.querySelectorAll('#tasks-kanban [id^="tasks-kanban-column-"]').forEach(col => {
    col.innerHTML = '<p class="text-gray-500 text-center py-8">Drop tasks here...</p>';
  });

  allTasks.forEach(task => {
    const column = document.getElementById(`tasks-kanban-column-${task.status}`);
    if (!column) return;

    const card = createTaskCard(task);
    column.appendChild(card);
  });

  initKanban('tasks-kanban', 'tasks-global', (taskId, newStatus) => {
    moveTask(taskId, newStatus, fetchAllTasks);
  });
}

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
    openEditModal(task);
  });

  return card;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Global refresh hook
window.refreshTasks = fetchAllTasks;

// KICK OFF THE EMPIRE — INITIAL FETCH ON PAGE LOAD
document.addEventListener('DOMContentLoaded', () => {
  console.log('tasks_global.js: DOM ready — initiating first fetch');
  fetchAllTasks();
});