// static/js/import_export.js
// TENET #1 OBEYED — NO INLINE JS. EVER.
// DATA OWNERSHIP CONTROLS — EXPORT/IMPORT DOMINATION

document.addEventListener('DOMContentLoaded', () => {
  const importInput = document.getElementById('header-import-input');
  if (!importInput) return;

  importInput.addEventListener('change', () => {
    const file = importInput.files[0];
    if (!file) return;

    const label = document.querySelector('label[for="header-import-input"] span');
    const originalText = label.textContent;
    label.textContent = 'RESTORING EMPIRE...';

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/import', {
      method: 'POST',
      body: formData
    })
      .then(r => r.json())
      .then(result => {
        alert(result.message || result.error || 'EMPIRE RESTORED, BROTHER!');
        if (!result.error) {
          setTimeout(() => location.reload(), 1500);
        }
      })
      .catch(err => {
        console.error('Import failed:', err);
        alert('IMPORT FAILED — CHECK THE CONSOLE, WARRIOR!');
      })
      .finally(() => {
        label.textContent = originalText;
        importInput.value = '';
      });
  });
});