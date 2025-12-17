// static/js/task_modal.js
// TASK MODAL + FULL CRUD LOGIC — UNIFIED WITH GOAL/EVENT PATTERN
// NO FORM, PURE JS CONTROL — TENET #4 ETERNAL

console.log('task_modal.js LOADED — MODAL DOMINATION CENTER ARMED');

if (window.taskModalInitialized) {
  console.log('task_modal.js already initialized — skipping');
} else {
  window.taskModalInitialized = true;

  const modal = document.getElementById('task-modal');
  if (!modal) {
    console.log('No #task-modal — safe skip');
    window.openTaskModal = () => {};
    window.openEditModal = () => {};
    window.closeTaskModal = () => {};
  } else {
    // ELEMENTS
    const saveBtn = document.getElementById('save-task-btn');
    const deleteBtn = document.getElementById('delete-task-btn');
    const closeBtn = document.getElementById('task-close-modal');
    const hiddenId = document.getElementById('task-id');

    // Recurring toggle
    document.getElementById('task-is-recurring')?.addEventListener('change', (e) => {
      document.getElementById('recurring-options')?.classList.toggle('hidden', !e.target.checked);
    });

    function openTaskModal() {
      modal.classList.remove('invisible', 'opacity-0');
      modal.classList.add('visible', 'opacity-100');
      document.getElementById('task-title')?.focus();
    }

    function closeTaskModal() {
      modal.classList.remove('visible', 'opacity-100');
      modal.classList.add('invisible', 'opacity-0');

      // Reset all fields
      modal.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach(el => {
        if (el.type === 'checkbox') el.checked = false;
        else el.value = '';
      });
      hiddenId.value = '';
      deleteBtn?.classList.add('hidden');
      document.getElementById('recurring-options')?.classList.add('hidden');
      const recurCheck = document.getElementById('task-is-recurring');
        if (recurCheck) recurCheck.checked = false;

    }

    function collectFormData() {
      const isRecurring = document.getElementById('task-is-recurring')?.checked || false;
      const calApp = document.getElementById('calendar-app');
      const isDayPage = calApp && calApp.dataset.year && calApp.dataset.month && calApp.dataset.day;

      let due_date = document.getElementById('task-due-date')?.value || null;
      if (isDayPage && !due_date) {
        const year = calApp.dataset.year;
        const month = String(calApp.dataset.month).padStart(2, '0');
        const day = String(calApp.dataset.day).padStart(2, '0');
        due_date = `${year}-${month}-${day}`;
      }

        return {
        title: document.getElementById('task-title')?.value.trim() || '',
        description: document.getElementById('task-description')?.value.trim() || null,
        due_date,
        priority: document.getElementById('task-priority')?.value || 'medium',
        tags: document.getElementById('task-tags')?.value.trim() || null,
        is_recurring: isRecurring,
        recurrence_type: isRecurring ? document.getElementById('task-recurrence-type')?.value : null,
        recurrence_interval: isRecurring ? parseInt(document.getElementById('task-recurrence-interval')?.value) || 1 : null,
        recurrence_end_date: isRecurring ? document.getElementById('task-recurrence-end')?.value || null : null,
        status: (!hiddenId.value && isDayPage) ? TASK_STATUS.TODO : undefined  // ← NEW: Force TODO on Day page new tasks
      };
    }

    function saveTask() {
      const taskId = hiddenId.value;
      const data = collectFormData();
      if (!data.title) return alert('Title required, warrior!');

      const method = taskId ? 'PATCH' : 'POST';
      const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';

      fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(() => {
        closeTaskModal();
        if (window.refreshTasks) window.refreshTasks();
      })
      .catch(err => console.error('Task save failed:', err));
    }

    // EDIT: populate + show DELETE
    window.openEditModal = function(task) {
      console.log('openEditModal CALLED — TASK OBJECT:', task);
      console.log('Priority value:', task.priority);
      console.log('Priority element:', document.getElementById('task-priority'));
      hiddenId.value = task.id || '';
      document.getElementById('task-title').value = task.title || '';
      document.getElementById('task-description').value = task.description || '';
      document.getElementById('task-due-date').value = task.due_date || '';
      document.getElementById('task-priority').value = task.priority || 'medium';
      document.getElementById('task-tags').value = task.tags || '';

      const recurCheck = document.getElementById('task-is-recurring');
      recurCheck.checked = !!task.is_recurring;
      document.getElementById('recurring-options').classList.toggle('hidden', !task.is_recurring);

      if (task.is_recurring) {
        const recurType = document.getElementById('task-recurrence-type');
        if (recurType) recurType.value = task.recurrence_type || 'daily';

        const recurInterval = document.getElementById('task-recurrence-interval');
        if (recurInterval) recurInterval.value = task.recurrence_interval || 1;

        const recurEnd = document.getElementById('task-recurrence-end');
        if (recurEnd) recurEnd.value = task.recurrence_end_date || '';

      }

      deleteBtn?.classList.remove('hidden');
      openTaskModal();
    };

    // + BUTTON — NEW TASK (GLOBAL OR DAY PAGE)
    document.getElementById('add-task-btn')?.addEventListener('click', () => {
      closeTaskModal(); // Full reset

      const calApp = document.getElementById('calendar-app');
      const isDayPage = calApp && calApp.dataset.year && calApp.dataset.month && calApp.dataset.day;

      if (isDayPage) {
        const year = calApp.dataset.year;
        const month = String(calApp.dataset.month).padStart(2, '0');
        const day = String(calApp.dataset.day).padStart(2, '0');
        const todayStr = `${year}-${month}-${day}`;
        document.getElementById('task-due-date').value = todayStr;
      }

      openTaskModal();
    });

    // BUTTON HANDLERS
    saveBtn.onclick = saveTask;
    deleteBtn.onclick = () => {
      if (!confirm('Obliterate this task forever?')) return;
      const taskId = hiddenId.value;
      fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
        .then(() => {
          closeTaskModal();
          if (window.refreshTasks) window.refreshTasks();
        });
    };
    closeBtn.onclick = closeTaskModal;

    // ENTER KEY SAVE (except Shift+Enter in textarea)
    modal.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        saveTask();
      }
    });

    // DELETE FROM CARD (delegated — works on any page)
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-task-delete');
      if (!btn) return;
      const card = btn.closest('.task-card');
      if (!card || !confirm('Obliterate this task forever?')) return;
      const taskId = card.dataset.id;
      fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
        .then(() => window.refreshTasks?.());
    });

    // GLOBAL EXPORTS
    window.openTaskModal = openTaskModal;
    window.closeTaskModal = closeTaskModal;
    window.openEditModal = openEditModal;
  }
}