// app/static/js/goals_kanban.js
// STEP 7 — TREE VIEW + COLLAPSE + KANBAN — FULLY FUNCTIONAL

let allGoals = [];

document.addEventListener('DOMContentLoaded', () => {
  fetchGoals();
  document.getElementById('add-goal-btn').addEventListener('click', openModal);
});

function fetchGoals() {
  fetch('/api/goals')
    .then(r => r.json())
    .then(goals => {
      allGoals = goals;
      renderTree(goals);
      renderKanban(goals);
    });
}

// TREE RENDERER
function renderTree(goals) {
  const container = document.getElementById('goal-tree');
  container.innerHTML = '';

  const buildTreeHtml = (node, level = 0) => {
    const indent = '&nbsp;'.repeat(level * 4);
    const toggle = node.children?.length ? `<span class="toggle cursor-pointer text-yellow-400 mr-2">[−]</span>` : '<span class="mr-6"></span>';
    const card = document.createElement('div');
    card.className = 'mb-2 p-3 bg-gray-700 rounded flex items-center';
    card.innerHTML = `
      ${toggle}
      <span class="font-medium">${escapeHtml(node.title)}</span>
      <span class="ml-auto text-sm text-gray-400">${node.category} • ${node.status} • ${node.progress}%</span>
    `;

    container.appendChild(card);

    if (node.children?.length) {
      const childrenDiv = document.createElement('div');
      childrenDiv.className = 'children ml-8';
      node.children.forEach(child => buildTreeHtml(child, level + 1));
      container.appendChild(childrenDiv);

      // Collapse/expand logic
      card.querySelector('.toggle').addEventListener('click', (e) => {
        const toggle = e.target;
        const isOpen = toggle.textContent === '[−]';
        toggle.textContent = isOpen ? '[+]' : '[−]';
        childrenDiv.style.display = isOpen ? 'none' : 'block';
      });
    }
  };

  goals.forEach(goal => buildTreeHtml(goal));
}

// Helper to flatten tree for Kanban
function flatGoals(nodes, result = []) {
  nodes.forEach(node => {
    result.push(node);
    if (node.children) flatGoals(node.children, result);
  });
  return result;
}

// KANBAN RENDERER — FIXED, ETERNAL, TENET-COMPLIANT
function renderKanban(goals) {
  // Clear all columns first
  document.querySelectorAll('#kanban [id]').forEach(col => col.innerHTML = '');

  const flatList = flatGoals(goals);

  console.log(`Rendering ${flatList.length} goals into Kanban...`);

  flatList.forEach(goal => {
    // CRITICAL FIX: status comes from ENUM as lowercase string already!
    const statusKey = goal.status; // 'doing', 'todo', etc.
    const column = document.getElementById(statusKey);
    
    if (!column) {
      console.warn(`No column found for status: ${statusKey}`, goal);
      return;
    }

    const card = document.createElement('div');
    card.className = 'goal-card bg-gray-800 p-5 rounded-xl cursor-move shadow-lg border-l-4 transition-all hover:scale-105 hover:shadow-2xl';
    card.dataset.id = goal.id;

    // TENET #3 OBEYED — COLOR COMES FROM SINGLE SOURCE OF TRUTH
    // NO MORE DUPLICATE OBJECTS. NO MORE MAGIC KEYS. NO MORE DRIFT.
    const color = window.CATEGORY_COLORS[goal.category] || 'gray';
    card.classList.add(`border-${color}-500`);

    card.innerHTML = `
    <div class="font-bold text-white text-xl mb-2">${escapeHtml(goal.title)}</div>
    <div class="text-sm text-gray-400 uppercase tracking-wider mb-3">${goal.category}</div>
    <div class="mt-4">
        <div class="bg-gray-700 rounded-full h-4 overflow-hidden border border-gray-600">
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 h-full transition-all duration-700" style="width: ${goal.progress}%"></div>
        </div>
        <div class="text-xs text-right text-gray-300 mt-2 font-bold">${goal.progress}%</div>
    </div>
    `;

    column.appendChild(card);
  });

  initSortable(); // Re-init after DOM update
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Modal functions
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
  if (!title) {
    alert("BROTHER — A GOAL WITHOUT A TITLE IS WEAKNESS!");
    return;
  }

  const payload = {
    title: title,
    description: document.getElementById('goal-description').value.trim(),
    category: document.getElementById('goal-category').value,
    due_date: document.getElementById('goal-due-date').value || null,
    is_habit: document.getElementById('goal-is-habit').checked
  };

  fetch('/api/goals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(() => {
    closeModal();
    fetchGoals();
  })
  .catch(err => {
    console.error("GOAL CREATION FAILED:", err);
    alert("SOMETHING WENT WRONG BROTHER — CHECK THE CONSOLE!");
  });
}

// Sortable.js — FIXED FOR 2025 DOMINATION
function initSortable() {
  // Destroy any existing instances first (prevents duplicate listeners)
  document.querySelectorAll('#kanban [id]').forEach(column => {
    if (column.sortable) {
      column.sortable.destroy();
    }
  });

  document.querySelectorAll('#kanban [id]').forEach(column => {
    column.sortable = new Sortable(column, {
      group: 'kanban',
      animation: 180,
      easing: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
      ghostClass: 'kanban-ghost',        // ← FIXED: No spaces!
      chosenClass: 'kanban-chosen',
      dragClass: 'kanban-dragging',
      
      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;

        const goalId = evt.item.dataset.id;
        const newStatus = Object.keys(GOAL_STATUS).find(
          key => key.toLowerCase() === evt.to.id
        ); // 'todo' → 'TODO'

        fetch(`/api/goals/${goalId}/move`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            status: newStatus 
          })
        })
        .then(r => {
          if (!r.ok) throw new Error('Move failed');
          return r.json();
        })
        .then(() => fetchGoals())
        .catch(err => {
          console.error('Move failed:', err);
          fetchGoals(); // Revert on failure
        });
      }
    });
  });
}