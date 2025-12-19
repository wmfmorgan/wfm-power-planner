// static/js/ics_sync.js — TENET #1 OBEYED — PURE EXTERNAL PROTEIN
document.getElementById('sync-ics-btn')?.addEventListener('click', (e) => {
  const btn = e.target;
  const datestr = btn.dataset.datestr;
  btn.disabled = true;
  btn.textContent = 'SYNCING...';

  fetch(`/api/import-calendar/${datestr}`)
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        // alert(data.message || `Sync complete — ${data.imported} new events added!`);
        if (window.refreshCalendarEvents) window.refreshCalendarEvents();
      } else {
        alert('Sync failed: ' + (data.error || 'unknown'));
      }
    })
    .catch(err => {
      console.error('ICS sync error:', err);
      alert('Sync failed — check connection or console');
    })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = 'SYNC';
    });
});