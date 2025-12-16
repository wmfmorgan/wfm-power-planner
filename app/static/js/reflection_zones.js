// static/js/reflection_zones.js
// Use single source of truth — Tenet #3 eternal
const NOTE_TYPES = Object.values(REFLECTION_NOTE_TYPE);

document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const timeframe = root.dataset.timeframe;        // now 'day', 'week', 'month'
    const dateStr = root.dataset.dateStr;            // '2025-12-16'

    if (!timeframe || !dateStr) return;

    // Load existing
    fetch(`/api/reflections/${timeframe}/${dateStr.replace(/-/g, '/')}`)
        .then(r => r.json())
        .then(data => {
            NOTE_TYPES.forEach(type => {
                const ta = document.querySelector(`textarea[name="${type}"]`);
                if (ta) ta.value = data[type] || '';
            });
        });

    // Save on blur
    NOTE_TYPES.forEach(type => {
        const ta = document.querySelector(`textarea[name="${type}"]`);
        if (!ta) return;

        ta.addEventListener('blur', () => {
            const content = ta.value.trim();
            fetch('/api/reflections', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: type,
                    timeframe: timeframe,
                    date: dateStr,
                    content: content
                })
            });
            // Victory glow
            ta.classList.add('border-green-400');
            setTimeout(() => ta.classList.remove('border-green-400'), 1000);
        });
    });
});