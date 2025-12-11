// static/js/tasks_kanban.js — PHASE 3.1 TASKS ENGINE — FULL CRUD + DRAG-AND-DROP
let allTasks = [];

document.addEventListener('DOMContentLoaded', () => {
  fetchTasks();
  document.getElementById('add-task-btn').addEventListener('click', openModal);
  document.getElementById('close-modal').addEventListener('click', closeModal);
  document.getElementById('task-form').addEventListener('submit', handleSubmit);
});

function fetchTasks() {
  fetch('/api/tasks')
    .then(r => r.json())
    .then(tasks => {
      allTasks = tasks;
      renderTasks();
    });
}

function renderTasks() {
  document.querySelectorAll('#tasks-kanban [id^="column-"]').forEach(col => col.innerHTML = '');
  allTasks.forEach(task => {
    const col = document.getElementById(`column-${task.status}`);
    if (!col) return;
    const card = document.createElement('div');
    card.className = 'bg-gray-800 pad rounded-lg shadow-lg cursor-move hover:scale-105 transition-all border-l-4 border-${getPriorityColor(task.priority)}-500';
    card.dataset.id = task.id;
    card.innerHTML = `
      <div class="font-bold text-lg text-white mb-2">${escapeHtml(task.title)}</div>
      <div class="text-sm text-gray-400 mb-4">${task.due_date || 'No due date'}</div>
      <div class="text-xs text-gray-500">${task.tags || ''}</div>
    </div>`;
    col.appendChild(card);
  });
  initSortable();
}

function initSortable() {
  document.querySelectorAll('#tasks-kanban [id^="column-"]').forEach(column => {
    if (column.sortable) column.sortable.destroy();
    column.sortable = new Sortable(column, {
      group: 'tasks',
      animation: 180,
      ghostClass: 'kanban-ghost',
      chosenClass: 'kanban-chosen',
      dragClass: 'kanban-dragging',
      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;
        const taskId = evt.item.dataset.id;
        const newStatus = evt.to.id.replace('column-', '');
        fetch(`/api/tasks/${taskId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        }).then(() => fetchTasks());
      }
    });
  });
}

function openModal() {
  document.getElementById('task-modal').classList.remove('invisible', 'opacity-0');
  document.getElementById('task-modal').classList.add('visible', 'opacity-100');
  document.getElementById('task-title').focus();
}

function closeModal() {
  document.getElementById('task-modal').classList.remove('visible', 'opacity-100');
  document.getElementById('task-modal').classList.add('invisible', 'opacity-0');
  document.getElementById('task-form').reset();
}

function handleSubmit(e) {
  e.preventDefault();
  const data = {
    title: document.getElementById('task-title').value.trim(),
    description: document.getElementById('task-description').value.trim(),
    due_date: document.getElementById('task-due-date').value || null,
    priority: document.getElementById('task-priority').value,
    tags: document.getElementById('task-tags').value.trim()
  };
  fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(() => {
    closeModal();
    fetchTasks();
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}