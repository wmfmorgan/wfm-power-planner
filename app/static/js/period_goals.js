// static/js/period_goals.js
// PHASE 6 — SHOW GOALS ON MONTH/WEEK/DAY — CLEAN, ETERNAL, NO INLINE JS
function buildPeriodApiUrl() {
  const app = document.getElementById('calendar-app') || document.body;
  const view = app.dataset.currentView;
  const year = app.dataset.year;
  const month = (app.dataset.month || '').padStart(2, '0');
  const day = (app.dataset.day || '').padStart(2, '0');

  if (view === 'day') {
    return `/api/goals/period/daily/${year}/${month}/${day}`;
  } else if (view === 'week') {
    return `/api/goals/period/weekly/${year}/${month}/${day}`;
  } else {
    return `/api/goals/period/monthly/${year}/${month}`;
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const kanban = document.getElementById('period-goals-kanban');
  if (!kanban) return;
    const app = document.getElementById('calendar-app') || document.body;
    const view = app.dataset.currentView;
    const year = app.dataset.year;
    const month = app.dataset.month;
    const day = app.dataset.day;

  fetch(buildPeriodApiUrl())
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(goals => {
        renderPeriodGoals(goals);
        initCalendarGoalSortable(); // pass URL for re-fetch
    })
    .catch(err => console.error('Failed to load period goals:', err));
});
/**
 * EXACTLY matches PostgreSQL: EXTRACT('week' FROM date) + EXTRACT('isoyear' FROM date)
 * Monday = first day of week
 * Week 1 = first week with ≥4 days in the new year
 */
function getPostgresISOWeek(dateInput) {
  const date = new Date(dateInput);
  date.setHours(0, 0, 0, 0);

  // Find Thursday of this week — Thursday determines the year
  const dayOfWeek = date.getDay(); // 0 = Sunday
  const thursdayOffset = dayOfWeek >= 4 ? dayOfWeek - 4 : dayOfWeek + 3;
  const thursday = new Date(date);
  thursday.setDate(date.getDate() + thursdayOffset);

  const yearOfThursday = thursday.getFullYear();

  // January 4th is always in week 1
  const jan4 = new Date(yearOfThursday, 0, 4);
  const thursdayOfWeek1 = new Date(jan4);
  thursdayOfWeek1.setDate(jan4.getDate() + (4 - jan4.getDay() + 7) % 7);

  // Calculate week number
  const diffInDays = Math.floor((thursday - thursdayOfWeek1) / 86400000);
  const week = Math.floor(diffInDays / 7) + 1;

  return {
    year: yearOfThursday,
    week: week
  };
}

function renderPeriodGoals(goals) {
  document.querySelectorAll('#period-goals-kanban [id^="column-"]').forEach(col => col.innerHTML = '');
  
  goals.forEach(goal => {
    const column = document.getElementById(`column-${goal.status}`);
    
    if (!column) return;

    const card = document.createElement('div');
    card.className = 'goal-card cursor-pointer hover:scale-105 bg-card p-5 rounded-xl shadow-lg border-l-4 cursor-move';
    card.dataset.id = goal.id;

    const color = window.CATEGORY_COLORS[goal.category] || 'gray';
    card.classList.add(`border-${color}-500`);

    card.innerHTML = `
      <div class="font-bold text-white text-xl">${goal.title}</div>
      <div class="text-sm text-muted mt-2">${goal.timeframe} • ${goal.category}</div>
    `;
    // In renderPeriodGoals — add click
    card.addEventListener('click', () => openGoalModal(goal.id));

    column.appendChild(card);
  });
}

// AFTER renderPeriodGoals finishes — ADD CLICK TO EDIT
document.querySelectorAll('.goal-card').forEach(card => {
  card.style.cursor = 'pointer';
  card.addEventListener('click', () => {
    const goalId = card.dataset.id;
    // Reuse the existing modal open logic from goals_kanban.js
    openGoalModal(goalId);
  });
});

function initCalendarGoalSortable() {

  document.querySelectorAll('#period-goals-kanban [id^="column-"]').forEach(column => {
    if (column.sortable) column.sortable.destroy();

    column.sortable = new Sortable(column, {
      group: 'calendar-goals',
      animation: 180,
      easing: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
      ghostClass: 'kanban-ghost',
      chosenClass: 'kanban-chosen',
      dragClass: 'kanban-dragging',

      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;

        const goalId = evt.item.dataset.id;
        const newStatus = evt.to.id.replace('column-', '');

        fetch(`/api/goals/${goalId}/move`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        })
        .then(r => {
          if (!r.ok) throw new Error('Status update failed');
          return r.json();
        })
        .then(() => {
          // Re-fetch with fresh URL
          fetch(buildPeriodApiUrl())
            .then(r => r.json())
            .then(goals => renderPeriodGoals(goals));
        })
        .catch(err => console.error('Status update failed:', err));
      }
    });
  });
}

function openGoalModal(goalId) {
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

      const saveBtn = document.getElementById('save-goal-btn');
      saveBtn.onclick = () => updateGoal(goal.id);

      const modal = document.getElementById('goal-modal');
      modal.classList.remove('invisible', 'opacity-0');
      modal.classList.add('visible', 'opacity-100');
      // ADD SUB-GOAL BUTTON — WORKS FROM ANYWHERE
      const addSubgoalBtn = document.getElementById('add-subgoal-btn');
      addSubgoalBtn.onclick = () => {
        const title = prompt("New step title:");
        if (!title?.trim()) return;

          let childTimeframe = 'monthly'; // fallback
            switch (goal.timeframe) {
                case 'yearly':
                childTimeframe = 'quarterly';
                break;
                case 'quarterly':
                childTimeframe = 'monthly';
                break;
                case 'monthly':
                childTimeframe = 'weekly';
                break;
                case 'weekly':
                childTimeframe = 'daily';
                break;
                case 'daily':
                childTimeframe = 'daily'; // can't go lower — stays daily
                break;
            }
        
        const payload = {
          title: title.trim(),
          parent_id: goal.id,
          due_date: goal.due_date,
          timeframe: childTimeframe,  // inherit parent's timeframe
          category: goal.category,
          status: 'todo'
        };

        fetch('/api/goals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        .then(() => {
          closeGoalModal();
          // Refresh current view
          location.reload();
        });
    };
});
}


function updateGoal(goalId) {
  const payload = {
    title: document.getElementById('goal-title').value.trim(),
    description: document.getElementById('goal-description').value.trim(),
    category: document.getElementById('goal-category').value,
    timeframe: document.getElementById('goal-timeframe').value,
    due_date: document.getElementById('goal-due-date').value || null,
    is_habit: document.getElementById('goal-is-habit').checked
  };

  fetch(`/api/goals/${goalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(() => {
    closeGoalModal();
    fetch(buildPeriodApiUrl()).then(r => r.json()).then(goals => renderPeriodGoals(goals));
  });
}

function closeGoalModal() {
  const modal = document.getElementById('goal-modal');
  modal.classList.add('invisible', 'opacity-0');
  modal.classList.remove('visible', 'opacity-100');
}

// Wire up the cancel button — once on load
document.addEventListener('DOMContentLoaded', () => {
  const cancelBtn = document.getElementById('close-goal-modal');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeGoalModal);
  }

  // Also close on background click
  const modal = document.getElementById('goal-modal');
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeGoalModal();
  });
});

function populateGoalModalSelects() {
  const categorySelect = document.getElementById('goal-category');
  const timeframeSelect = document.getElementById('goal-timeframe');

  // Clear
  categorySelect.innerHTML = '';
  timeframeSelect.innerHTML = '';

  // Category
  Object.values(GOAL_CATEGORY).forEach(value => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = value.charAt(0).toUpperCase() + value.slice(1);
    categorySelect.appendChild(opt);
  });

  // Timeframe
  Object.values(GOAL_TIMEFRAMES).forEach(value => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = value.charAt(0).toUpperCase() + value.slice(1);
    timeframeSelect.appendChild(opt);
  });
}

// Run once on load
document.addEventListener('DOMContentLoaded', populateGoalModalSelects);