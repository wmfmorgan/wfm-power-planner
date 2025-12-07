// app/static/js/goals_kanban.js
// TENET #1 OBEYED — NO INLINE JS
// TENET #30 OBEYED — SortableJS ONLY

document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/goals')
    .then(r => r.json())
    .then(data => renderGoals(data));
});

function renderGoals(goals) {
  goals.forEach(goal => {
    const card = createGoalCard(goal);
    document.getElementById(goal.status.toLowerCase()).appendChild(card);
  });

  // Initialize SortableJS on all columns
  document.querySelectorAll('#kanban > div > div[id]').forEach(column => {
    new Sortable(column, {
      group: 'kanban',
      animation: 150,
      ghostClass: 'bg-gray-900 opacity-50',
      onEnd: handleDrop
    });
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
  const map = {
    'MARITAL': 'pink', 'SOCIAL': 'purple', 'FINANCIAL': 'yellow',
    'WORK': 'blue', 'FAMILY': 'orange', 'SPIRITUAL': 'indigo',
    'HEALTH': 'green', 'HOBBY': 'red'
  };
  return map[cat] || 'gray';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function handleDrop(evt) {
  const goalId = evt.item.dataset.id;
  const newStatus = evt.to.id.toUpperCase();
  console.log('Goal moved:', goalId, '→', newStatus);
  // Phase 3: send to backend
}