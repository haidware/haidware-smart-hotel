document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  if (toggle) toggle.onclick = () => sidebar.classList.toggle('open');

  document.addEventListener('click', e => {
    if (window.innerWidth <= 900 && sidebar && sidebar.classList.contains('open')
        && !sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  });

  const search = document.getElementById('globalSearch');
  if (search) {
    search.oninput = e => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('.search-target').forEach(x => {
        x.style.display = x.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    };
  }

  document.querySelectorAll('.filter-btn').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.filter-btn').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      document.querySelectorAll('.filter-row').forEach(r => {
        r.classList.toggle('hidden-by-filter',
          b.dataset.category !== 'All' && r.dataset.category !== b.dataset.category);
      });
    };
  });

  document.querySelectorAll('.toggle input').forEach(i => {
    i.onchange = () => {
      const s = i.closest('.toggle').querySelector('span');
      const isStatusToggle = ['Active', 'Inactive'].includes(s.textContent.trim());
      s.textContent = isStatusToggle
        ? (i.checked ? 'Active' : 'Inactive')
        : (i.checked ? 'Visible on Device' : 'Hidden from Device');
      toast('Updated locally. No database request was made.');
    };
  });

  document.querySelectorAll('.device-action').forEach(b => {
    b.onclick = () => toast(`${b.dataset.action} command prepared for ${b.dataset.device}. Backend not connected.`);
  });

  const save = document.getElementById('saveSettings');
  if (save) save.onclick = () => toast('Settings saved in the interface only.');

  const exp = document.getElementById('exportButton');
  if (exp) exp.onclick = () => exportCsv();

  document.querySelectorAll('form').forEach(f => {
    f.onsubmit = e => {
      e.preventDefault();
      toast('Foundation form — persistence will be added with the database layer.');
    };
  });
});

function toast(m) {
  document.querySelector('.toast')?.remove();
  const d = document.createElement('div');
  d.className = 'toast';
  d.textContent = m;
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 3200);
}

function exportCsv() {
  const t = document.getElementById('exportTable');
  if (!t) return;
  const rows = [...t.querySelectorAll('tr')].map(r =>
    [...r.querySelectorAll('th,td')].slice(0, -1)
      .map(c => '"' + c.innerText.replace(/"/g, '""').trim() + '"').join(',')
  );
  const u = URL.createObjectURL(new Blob([rows.join('\n')], { type: 'text/csv' }));
  const a = document.createElement('a');
  a.href = u; a.download = 'haidware-orders.csv'; a.click();
  URL.revokeObjectURL(u);
  toast('Orders CSV exported.');
}
