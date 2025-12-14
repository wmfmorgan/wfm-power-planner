// static/js/task_modal.js
// TASK MODAL + FULL CRUD LOGIC — EXTRACTED FOR REUSE
// Used by both global Tasks page and Day page — zero duplication
// Championship comments — future warriors in 2035 will feel the power

console.log('task_modal.js LOADED — MODAL DOMINATION CENTER ARMED');

// SINGLE INITIALIZATION GUARD — PREVENTS DOUBLE-RUN IF LOADED TWICE
if (window.taskModalInitialized) {
  console.log('task_modal.js already initialized — skipping duplicate run');
} else {
  window.taskModalInitialized = true;

  const modal = document.getElementById('task-modal');

  if (!modal) {
    console.log('task_modal.js: No #task-modal in DOM — safe to skip init (e.g. Goals page)');
    // Stub globals so other scripts don't crash if they call early
    window.openTaskModal = () => console.warn('Task modal not available on this page');
    window.openEditModal = () => console.warn('Task modal not available on this page');
    window.closeTaskModal = () => console.warn('Task modal not available on this page');
  } else {
    // ONLY RUN FULL INIT WHEN MODAL EXISTS
    const form = document.getElementById('task-form');
    const closeBtn = document.getElementById('task-close-modal');

    // Recurring toggle — safe optional chaining
    document.getElementById('task-is-recurring')?.addEventListener('change', (e) => {
      const options = document.getElementById('recurring-options');
      if (options) options.classList.toggle('hidden', !e.target.checked);
    });

    function openTaskModal() {
      modal.classList.remove('invisible', 'opacity-0');
      modal.classList.add('visible', 'opacity-100');
      document.getElementById('task-title')?.focus();
    }

    function closeTaskModal() {
      modal.classList.remove('visible', 'opacity-100');
      modal.classList.add('invisible', 'opacity-0');
      form.reset();
      form.removeAttribute('data-task-id');
      form.onsubmit = handleCreate;
      const options = document.getElementById('recurring-options');
      if (options) options.classList.add('hidden');
    }

    function collectFormData() {
      const isRecurring = document.getElementById('task-is-recurring')?.checked || false;
      return {
        title: document.getElementById('task-title')?.value.trim() || '',
        description: document.getElementById('task-description')?.value.trim() || null,
        due_date: document.getElementById('task-due-date')?.value || null,
        priority: document.getElementById('task-priority')?.value || 'medium',
        tags: document.getElementById('task-tags')?.value.trim() || null,
        is_recurring: isRecurring,
        recurrence_type: isRecurring ? document.getElementById('task-recurrence-type')?.value : null,
        recurrence_interval: isRecurring ? parseInt(document.getElementById('task-recurrence-interval')?.value) || 1 : null,
        recurrence_end_date: isRecurring ? document.getElementById('task-recurrence-end')?.value || null : null
      };      
    }

    function handleCreate(e) {
      e.preventDefault();
      const data = collectFormData();
      fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(() => {
        closeTaskModal();
        if (window.refreshTasks) window.refreshTasks();
      })
      .catch(err => console.error('Create failed:', err));
    }

    function handleUpdate(e) {
      e.preventDefault();
      const taskId = form.dataset.taskId;
      if (!taskId) return;

      const data = collectFormData();
      fetch(`/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(() => {
        closeTaskModal();
        if (window.refreshTasks) window.refreshTasks();
      })
      .catch(err => console.error('Update failed:', err));
    }

    window.openEditModal = function(task) {
      // Populate fields
      const titleEl = document.getElementById('task-title');
      const descEl = document.getElementById('task-description');
      const dueEl = document.getElementById('task-due-date');
      const priEl = document.getElementById('task-priority');
      const tagsEl = document.getElementById('task-tags');

      if (titleEl) titleEl.value = task.title || '';
      if (descEl) descEl.value = task.description || '';
      if (dueEl) dueEl.value = task.due_date || '';
      if (priEl) priEl.value = task.priority || 'medium';
      if (tagsEl) tagsEl.value = task.tags || '';

      // Recurring
      const recurCheck = document.getElementById('task-is-recurring');
      const options = document.getElementById('recurring-options');
      if (recurCheck) recurCheck.checked = !!task.is_recurring;
      if (options) options.classList.toggle('hidden', !task.is_recurring);

      if (task.is_recurring) {
        const typeEl = document.getElementById('task-recurrence-type');
        const intervalEl = document.getElementById('task-recurrence-interval');
        const endEl = document.getElementById('task-recurrence-end');

        if (typeEl) typeEl.value = task.recurrence_type || 'daily';
        if (intervalEl) intervalEl.value = task.recurrence_interval || 1;
        if (endEl) endEl.value = task.recurrence_end_date || '';
      }

      form.dataset.taskId = task.id;
      form.onsubmit = handleUpdate;
      openTaskModal();
    };

    // Delete delegation — works on any page with task cards
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-task-delete');
      if (!btn) return;

      const card = btn.closest('.task-card');
      if (!card || !confirm('Obliterate this task forever?')) return;

      const taskId = card.dataset.id;
      if (!taskId) return;

      fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
        .then(() => {
          if (window.refreshTasks) window.refreshTasks();
        })
        .catch(err => console.error('Delete failed:', err));
    });

    // Global exports
    Object.assign(window, {
      openTaskModal,
      closeTaskModal,
      openEditModal
    });

    // + BUTTON LISTENER — WORKS ON ANY PAGE WITH #add-task-btn
    // Global Tasks page AND Day page both have the floating yellow beast
    document.getElementById('add-task-btn')?.addEventListener('click', () => {
        // Reset form for new task
        form.reset();
        form.removeAttribute('data-task-id');
        form.onsubmit = handleCreate;
        document.getElementById('recurring-options')?.classList.add('hidden');
        const recurCheckbox = document.getElementById('task-is-recurring');
        if (recurCheckbox) {
            recurCheckbox.checked = false;
        }
        openTaskModal();
    });


    // Final setup — safe because we're inside the modal-exists branch
    if (form) form.onsubmit = handleCreate;
    if (closeBtn) closeBtn.addEventListener('click', closeTaskModal);
  }
}    