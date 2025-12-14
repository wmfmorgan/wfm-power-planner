// static/js/kanban_core.js
// SHARED KANBAN ENGINE — TENET #13 ETERNAL LAW
// One source for all drag-and-drop behavior across Tasks (global + day)
// Championship comments — future warriors in 2035 will know exactly what this owns

console.log('kanban_core.js LOADED — UNIFIED DRAG ENGINE ARMED');

/**
 * Initializes SortableJS on all columns within a kanban container
 * @param {string} kanbanId - The ID of the parent kanban div (e.g. 'tasks-kanban' or 'day-tasks-kanban')
 * @param {string} groupName - Sortable group name (prevents cross-kanban drag)
 * @param {function} onMove - Callback: (taskId: string, newStatus: string) => void
 */
function initKanban(kanbanId, groupName, onMove) {
  const container = document.getElementById(kanbanId);
  if (!container) return;

  // Destroy existing instances to prevent memory leaks / duplicate handlers
  container.querySelectorAll('[id^="column-"]').forEach(col => {
    if (col.sortableInstance) {
      col.sortableInstance.destroy();
    }
  });

  container.querySelectorAll(`#${kanbanId} [id^="${kanbanId}-column-"]`).forEach(column => {
    column.sortableInstance = new Sortable(column, {
      group: groupName,
      animation: 180,
      easing: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
      ghostClass: 'kanban-ghost',
      chosenClass: 'kanban-chosen',
      dragClass: 'kanban-dragging',
      cursor: 'grabbing',

      onEnd: (evt) => {
        if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;

        const taskId = evt.item.dataset.id;
        const newStatus = evt.to.id.replace(`${kanbanId}-column-`, '');

        if (taskId && newStatus) {
          onMove(taskId, newStatus);
        }
      }
    });
  });
}

/**
 * Standardizes task status move API call
 * @param {string} taskId
 * @param {string} newStatus
 * @param {function} refreshCallback - Called after successful move
 */
function moveTask(taskId, newStatus, refreshCallback) {
  fetch(`/api/tasks/${taskId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  })
  .then(r => {
    if (!r.ok) throw new Error('Move failed');
    return r;
  })
  .then(() => refreshCallback())
  .catch(err => {
    console.error('Task move failed:', err);
    alert('Failed to update task status. Check console.');
    refreshCallback(); // Still refresh to stay in sync
  });
}

// Expose to global scope for context scripts
Object.assign(window, {
  initKanban,
  moveTask
});