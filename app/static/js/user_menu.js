// static/js/user_menu.js — TENET #1 OBEYED — NO INLINE JS EVER!
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('user-menu-toggle');
  const menu = document.getElementById('user-menu');
  const arrow = document.getElementById('user-menu-arrow');

  if (!toggle || !menu || !arrow) return;

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = menu.classList.contains('opacity-100');
    
    menu.classList.toggle('opacity-0', isOpen);
    menu.classList.toggle('invisible', isOpen);
    menu.classList.toggle('opacity-100', !isOpen);
    menu.classList.toggle('visible', !isOpen);
    menu.classList.toggle('pointer-events-auto', !isOpen);
    menu.classList.toggle('pointer-events-none', isOpen);
    
    arrow.classList.toggle('rotate-180', !isOpen);
  });

  // Close when clicking outside
  document.addEventListener('click', () => {
    menu.classList.add('opacity-0', 'invisible', 'pointer-events-none');
    menu.classList.remove('opacity-100', 'visible', 'pointer-events-auto');
    arrow.classList.remove('rotate-180');
  });
});