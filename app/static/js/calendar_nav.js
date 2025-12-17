// static/js/calendar_nav.js
// CALENDAR NAVIGATION — PURE PROTEIN, NO INLINE JS, WORKS OFFLINE
document.addEventListener('DOMContentLoaded', () => {
  const currentView = document.documentElement.dataset.currentView || 'month';
  const year = parseInt(document.documentElement.dataset.year) || new Date().getFullYear();
  const month = parseInt(document.documentElement.dataset.month) || new Date().getMonth() + 1;
  const day = parseInt(document.documentElement.dataset.day) || new Date().getDate();

  // Highlight active button
  document.querySelectorAll('[data-view]').forEach(btn => {
    if (btn.dataset.view === currentView) {
      btn.classList.add('active');
    }
    btn.addEventListener('click', () => navigate(btn.dataset.view));
  });

  document.getElementById('nav-today').addEventListener('click', () => {
    const today = new Date();
    navigate('day', today.getFullYear(), today.getMonth()+1, today.getDate());
  });

  // POWER MOVE: If we land on plain /calendar → snap to browser-local TODAY day view
  if (window.location.pathname === '/calendar' || window.location.pathname === '/calendar/') {
    const today = new Date();
    navigate('day', today.getFullYear(), today.getMonth() + 1, today.getDate());
  }

  function navigate(view, y = year, m = month, d = day) {
    const url = `/calendar/${view}/${y}${m !== undefined ? '/' + m : ''}${d !== undefined ? '/' + d : ''}`;
    history.pushState({view, year: y, month: m, day: d}, '', url);
    document.documentElement.dataset.currentView = view;
    document.documentElement.dataset.year = y;
    document.documentElement.dataset.month = m;
    document.documentElement.dataset.day = d;

    // Future: we'll swap content via fetch() here
    // For now — full reload is acceptable (Step 2.1 = nav only)
    location.reload();
  }

  // Handle back/forward buttons
  window.addEventListener('popstate', (e) => {
    if (e.state) {
      location.reload();
    }
  });
});