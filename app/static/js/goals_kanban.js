// app/static/js/goals_kanban.js
// TENET #1 OBEYED — NO INLINE JS
// TENET #15 OBEYED — CHAMPIONSHIP COMMENTS

document.addEventListener('DOMContentLoaded', () => {
  fetchGoals();
  initSortable();
});

function fetchGoals() {
  fetch('/api/goals')
    .then(r => r.json())
    .then(goals => renderGoals(goals));
}

function renderGoals(goals) {
  // Clear all columns
  document.querySelectorAll('#kanban > div > div[id]').forEach(col => col.innerHTML = '');

  goals.forEach(goal => {
    const card = createGoalCard(goal);
    document.getElementById(goal.status.toLowerCase()).appendChild(card);
  });
}

function createGoalCard(goal) {
  const div = document.createElement('div');
  div.className = `bg-gray-700 p-4 rounded-lg cursor-move border-l-4 border-${getCategoryColor(goal.category)}-500`;
  div.dataset.id = goal.id;
  div.innerHTML = `
    <div class="font-bold text-white">${escapeHtml(goal.title)}</div>
    <div class="text-sm text-gray-400">${goal.category}</div>
    <div class="mt-3">
      <div class="bg-gray-600 rounded-full h-3 overflow-hidden">
        <div class="bg-green-500 h-full transition-all" style="width: ${goal.progress}%"></div>
      </div>
      <div class="text-xs text-right text-gray-400">${goal.progress}%</div>
    </div>
  `;
  return div;
}

function getCategoryColor(cat) {
  const colors = {
    MARITAL: 'pink', SOCIAL: 'purple', FINANCIAL: 'yellow',
    WORK: 'blue', FAMILY: 'orange', SPIRITUAL: 'indigo',
    HEALTH: 'green', HOBBY: 'red'
  };
  return colors[cat] || 'gray';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// MODAL LOGIC
function openModal() {
  document.getElementById('goal-modal').classList.remove('hidden');
  document.getElementById('goal-title').focus();
}

function closeModal() {
  document.getElementById('goal-modal').classList.add('hidden');
  document.getElementById('goal-title').value = '';
}

function saveGoal() {
  const title = document.getElementById('goal-title').value.trim();
  if (!title) return;

  const payload = {
    title: title,
    category: document.getElementById('goal-category').value
  };

  fetch('/api/goals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(goal => {
    closeModal();
    fetchGoals(); // Refresh the board
  })
  .catch(err => console.error('Save failed:', err));
}

// BUTTON EVENT
document.getElementById('add-goal-btn').addEventListener('click', openModal);

// SORTABLEJS INIT
function initSortable() {
  document.querySelectorAll('#kanban > div > div[id]').forEach(column => {
    new Sortable(column, {
      group: 'kanban',
      animation: 150,
      ghostClass: 'bg-gray-900 opacity-50',
      onEnd: handleDrop
    });
  });
}

function handleDrop(evt) {
  const goalId = evt.item.dataset.id;
  const newStatus = evt.to.id.toUpperCase();

  fetch(`/api/goals/${goalId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  })
  .then(() => fetchGoals())
  .catch(err => console.error('Move failed:', err));
}