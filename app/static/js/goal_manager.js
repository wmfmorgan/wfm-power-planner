// static/js/goal_manager.js
// ETERNAL GOAL UI MANAGER — TREE + MODAL + CALENDAR KANBAN — SINGLE SOURCE OF TRUTH
// Tenets #1, #3, #11, #15, #17 — OBEYED FOREVER

const GOAL_MODAL = document.getElementById('goal-modal');

document.addEventListener('DOMContentLoaded', () => {
  // Tree page delegation (toggle, delete, add-child, inline edits)
  const tree = document.getElementById('goal-tree');
  if (tree) {
    setupTreeDelegation();
    restoreExpandedState();   // ← NEW: bring back warrior's last view
  }

  // Calendar goal kanban init
  const periodKanban = document.getElementById('period-goals-kanban');
  if (periodKanban) {
    fetchGoalsForPeriod().then(goals => {
      renderPeriodGoals(goals);
      initCalendarGoalSortable();
    });
  }

  // Global modal background close
  GOAL_MODAL?.addEventListener('click', (e) => {
    if (e.target === GOAL_MODAL) closeGoalModal();
  });
});

function populateGoalModalSelects() {
  const categorySelect = document.getElementById('goal-category');
  const timeframeSelect = document.getElementById('goal-timeframe');

  // Clear existing options (except we keep nothing — rebuild fresh)
  categorySelect.innerHTML = '';
  timeframeSelect.innerHTML = '';

  // CATEGORY — from global constants (loaded in base.html)
  Object.values(GOAL_CATEGORY).forEach(value => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = value.charAt(0).toUpperCase() + value.slice(1);
    categorySelect.appendChild(opt);
  });

  // TIMEFRAME — from global constants
  Object.values(GOAL_TIMEFRAMES).forEach(value => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = value.charAt(0).toUpperCase() + value.slice(1);
    timeframeSelect.appendChild(opt);
  });
}

function setupTreeDelegation() {
  const tree = document.getElementById('goal-tree');

  tree.addEventListener('click', (e) => {
    const actionEl = e.target.closest('[data-action]');
    if (!actionEl) return;

    const goalItem = actionEl.closest('.goal-item');
    const goalId = goalItem?.dataset.id;

    switch (actionEl.dataset.action) {
      case 'toggle':
        toggleGoalExpansion(goalId);
        saveExpandedState();
        break;
      case 'add-child':
        addChildGoal(goalId);
        break;
      case 'delete':
        if (confirm("BROTHER — DELETE THIS GOAL AND ALL SUBGOALS FOREVER? NO RECOVERY!")) {
          fetch(`/api/goals/${goalId}`, { method: 'DELETE' })
            .then(() => location.reload());
        }
        break;
    }
  });

  // Inline field changes
  tree.addEventListener('change', (e) => {
    const input = e.target;
    if (!input.matches('[data-field]')) return;

    const goalId = input.closest('.goal-item').dataset.id;
    const field = input.dataset.field;
    let value = input.type === 'checkbox' ? input.checked : input.value;
    if (field === 'due_date' && value === '') value = null;

    updateGoalField(goalId, field, value);
  });

  // Add root goal button
  document.getElementById('add-goal-btn')?.addEventListener('click', () => openGoalModal());
}

function toggleGoalExpansion(goalId) {
  const item = document.querySelector(`.goal-item[data-id="${goalId}"]`);
  const expanded = item.querySelector('.goal-expanded');
  const icon = item.querySelector('.toggle-icon');
  expanded.classList.toggle('hidden');
  icon.textContent = expanded.classList.contains('hidden') ? '▶' : '▼';
}

function updateGoalField(goalId, field, value) {
  const payload = { [field]: value };
  fetch(`/api/goals/${goalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(() => location.reload()); // Simple refresh — tree stays server-rendered
}

// ========================================
// MODAL — SHARED ACROSS ALL PAGES
// ========================================
function openGoalModal(goalId = null) {
  if (!GOAL_MODAL) return;

  // === ALWAYS REBUILD SELECTS FROM CONSTANTS ===
  populateGoalModalSelects();

  // Reset form
  document.getElementById('goal-id').value = '';
  document.getElementById('goal-title').value = '';
  document.getElementById('goal-description').value = '';
  document.getElementById('goal-category').value = 'work';
  document.getElementById('goal-timeframe').value = 'monthly';
  document.getElementById('goal-due-date').value = '';
  document.getElementById('goal-is-habit').checked = false;
  document.getElementById('modal-goal-tree').innerHTML = '';

  if (goalId) {
    fetch(`/api/goals/${goalId}`)
      .then(r => r.json())
      .then(goal => {
        document.getElementById('goal-id').value = goal.id;
        document.getElementById('goal-title').value = goal.title;
        document.getElementById('goal-description').value = goal.description || '';
        document.getElementById('goal-category').value = goal.category;
        document.getElementById('goal-timeframe').value = goal.timeframe;
        document.getElementById('goal-due-date').value = goal.due_date || '';
        document.getElementById('goal-is-habit').checked = goal.is_habit;

        // Load children
        fetch(`/api/goals/${goalId}/children`)
          .then(r => r.json())
          .then(children => renderModalChildren(children));
      });
  }

  // === CRITICAL: ATTACH SAVE/CANCEL HANDLERS HERE ===
  const saveBtn = document.getElementById('save-goal-btn');
  const cancelBtn = document.getElementById('close-goal-modal');

  saveBtn.onclick = () => saveGoalModal();
  cancelBtn.onclick = () => closeGoalModal();

  // Add subgoal button
  document.getElementById('add-subgoal-btn')?.replaceWith(
    document.getElementById('add-subgoal-btn').cloneNode(true) // Remove old listeners
  );
  document.getElementById('add-subgoal-btn')?.addEventListener('click', () => {
    const parentId = document.getElementById('goal-id').value;
    if (!parentId) return alert("Save parent goal first, brother!");
    addChildGoal(parentId, true); // true = in modal
  });

  GOAL_MODAL.classList.remove('invisible', 'opacity-0');
  GOAL_MODAL.classList.add('visible', 'opacity-100');
}

function closeGoalModal() {
  GOAL_MODAL?.classList.add('invisible', 'opacity-0');
  GOAL_MODAL?.classList.remove('visible', 'opacity-100');
}

function saveGoalModal() {
  const goalId = document.getElementById('goal-id').value;
  const payload = {
    title: document.getElementById('goal-title').value.trim(),
    description: document.getElementById('goal-description').value.trim(),
    category: document.getElementById('goal-category').value,
    timeframe: document.getElementById('goal-timeframe').value,
    due_date: document.getElementById('goal-due-date').value || null,
    is_habit: document.getElementById('goal-is-habit').checked
  };

  if (!payload.title) return alert("Title required, warrior!");

  const method = goalId ? 'PATCH' : 'POST';
  const url = goalId ? `/api/goals/${goalId}` : '/api/goals';

  fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(() => {
    closeGoalModal();
    if (document.getElementById('goal-tree')) {
      location.reload();
    } else {
      // Calendar page — refresh period goals
      fetchGoalsForPeriod().then(goals => renderPeriodGoals(goals));
    }
  });
}

function addChildGoal(parentId, inModal = false) {
  const title = prompt("New step title:");
  if (!title?.trim()) return;

  // Inherit timeframe one level down
  fetch(`/api/goals/${parentId}`)
    .then(r => r.json())
    .then(parent => {
      let childTimeframe = 'monthly';
      const map = { yearly: 'quarterly', quarterly: 'monthly', monthly: 'weekly', weekly: 'daily', daily: 'daily' };
      childTimeframe = map[parent.timeframe] || 'monthly';

      const payload = {
        title: title.trim(),
        parent_id: parentId,
        due_date: parent.due_date,
        category: parent.category,
        timeframe: childTimeframe,
        status: 'todo'
      };

      fetch('/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(() => {
        if (inModal) closeGoalModal();
        location.reload();
      });
    });
}

function renderModalChildren(children) {
  const container = document.getElementById('modal-goal-tree');
  container.innerHTML = '';
  children.forEach(child => {
    const div = document.createElement('div');
    div.className = 'bg-gray-800 rounded-lg p-4 mb-4 cursor-pointer hover:bg-gray-700 border-l-4 border-yellow-400';
    div.innerHTML = `
      <div class="font-bold text-white">${child.title}</div>
      <div class="text-sm text-gray-400">${child.timeframe} • ${child.status}</div>
    `;
    div.onclick = () => openGoalModal(child.id);
    container.appendChild(div);
  });
}

// ========================================
// CALENDAR PERIOD GOALS
// ========================================
function fetchGoalsForPeriod() {
  const app = document.getElementById('calendar-app') || document.body;
  const view = app.dataset.currentView;        // "day" | "week" | "month"
  const year = app.dataset.year;
  const month = app.dataset.month?.padStart(2, '0');
  const day = app.dataset.day?.padStart(2, '0');

  // MAP VIEW → ENUM VALUE — SINGLE SOURCE OF TRUTH
  const timeframeMap = {
    day:   'daily',
    week:  'weekly',
    month: 'monthly'
  };

  const timeframe = timeframeMap[view];
  if (!timeframe) {
    console.error('Invalid view for period goals:', view);
    return Promise.resolve([]);
  }

  let url = `/api/goals/period/${timeframe}/${year}`;
  if (month) url += `/${month}`;
  if (day)   url += `/${day}`;

  return fetch(url)
    .then(r => {
      if (!r.ok) {
        console.error('Period goals fetch failed:', r.status, r.statusText);
        throw new Error(`HTTP ${r.status}`);
      }
      return r.json();
    })
    .catch(err => {
      console.error('fetchGoalsForPeriod error:', err);
      return []; // Graceful fallback — no crash
    });
}                                                                                   

function renderPeriodGoals(goals) {
  document.querySelectorAll('#period-goals-kanban [id^="period-goals-kanban-column-"]').forEach(col => col.innerHTML = '');

  goals.forEach(goal => {
    const column = document.getElementById(`period-goals-kanban-column-${goal.status}`);
    if (!column) return;

    const card = document.createElement('div');
    card.className = 'goal-card cursor-pointer hover:scale-105 bg-card p-5 rounded-xl shadow-lg border-l-4 cursor-move';
    card.dataset.id = goal.id;
    card.classList.add(`border-${window.CATEGORY_COLORS?.[goal.category] || 'gray'}-500`);

    card.innerHTML = `
      <div class="font-bold text-white text-xl">${goal.title}</div>
      <div class="text-sm text-muted mt-2">${goal.timeframe} • ${goal.category}</div>
    `;
    card.addEventListener('click', () => openGoalModal(goal.id));
    column.appendChild(card);
  });
}

function initCalendarGoalSortable() {
  document.querySelectorAll('#period-goals-kanban [id^="period-goals-kanban-column-"]').forEach(column => {
    if (column.sortable) column.sortable.destroy();

    column.sortable = new Sortable(column, {
      group: 'calendar-goals',
      animation: 180,
      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;
        const goalId = evt.item.dataset.id;
        const newStatus = evt.to.id.replace('period-goals-kanban-column-', '');

        fetch(`/api/goals/${goalId}/move`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        }).then(() => fetchGoalsForPeriod().then(goals => renderPeriodGoals(goals)));
      }
    });
  });
}

// Save current open state to localStorage
function saveExpandedState() {
  const openIds = Array.from(document.querySelectorAll('.goal-item .goal-expanded:not(.hidden)'))
                       .map(el => el.closest('.goal-item').dataset.id);
  localStorage.setItem('goal-tree-open', JSON.stringify(openIds));
}

// Restore open state from localStorage
function restoreExpandedState() {
  const stored = localStorage.getItem('goal-tree-open');
  if (!stored) return;

  try {
    const openIds = JSON.parse(stored);
    openIds.forEach(id => {
      const item = document.querySelector(`.goal-item[data-id="${id}"]`);
      if (item) {
        const expanded = item.querySelector('.goal-expanded');
        const icon = item.querySelector('.toggle-icon');
        if (expanded && icon) {
          expanded.classList.remove('hidden');
          icon.textContent = '▼';
        }
      }
    });
  } catch (e) {
    console.warn('Failed to restore goal tree state');
  }
}
document.getElementById('collapse-all')?.addEventListener('click', () => {
  document.querySelectorAll('.goal-expanded').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.toggle-icon').forEach(icon => {
    if (icon.closest('.goal-item').querySelector('.children > *')) icon.textContent = '▶';
  });
  localStorage.removeItem('goal-tree-open');
});