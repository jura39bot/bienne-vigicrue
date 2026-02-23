const BASE = '/api/v1';

async function fetchJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function loadLatest() {
  try {
    const d = await fetchJSON(`${BASE}/debit/latest`);
    document.getElementById('latest-card').innerHTML = `
      <div class="value">${d.debit_moyen.toFixed(3)} m³/s</div>
      <div class="label">Débit moyen journalier — ${d.date}</div>
      ${d.debit_min != null ? `<div class="label">Min : ${d.debit_min.toFixed(3)} | Max : ${d.debit_max.toFixed(3)}</div>` : ''}
    `;
  } catch(e) {
    document.getElementById('latest-card').textContent = 'Données non disponibles';
  }
}

async function loadStats() {
  try {
    const s = await fetchJSON(`${BASE}/debit/stats?jours=30`);
    document.getElementById('stats-grid').innerHTML = `
      <div class="stat-card"><div class="val">${s.debit_moyen.toFixed(3)}</div><div class="lbl">Moy. m³/s</div></div>
      <div class="stat-card"><div class="val">${s.debit_min.toFixed(3)}</div><div class="lbl">Min m³/s</div></div>
      <div class="stat-card"><div class="val">${s.debit_max.toFixed(3)}</div><div class="lbl">Max m³/s</div></div>
    `;
  } catch(e) {
    document.getElementById('stats-grid').textContent = 'Données non disponibles';
  }
}

async function loadHistory() {
  try {
    const list = await fetchJSON(`${BASE}/debit/?limit=30`);
    const tbody = document.getElementById('history-body');
    if (!list.length) { tbody.innerHTML = '<tr><td colspan="4">Aucune donnée</td></tr>'; return; }
    tbody.innerHTML = list.map(d => `
      <tr>
        <td>${d.date}</td>
        <td><strong>${d.debit_moyen.toFixed(3)}</strong></td>
        <td>${d.debit_min != null ? d.debit_min.toFixed(3) : '-'}</td>
        <td>${d.debit_max != null ? d.debit_max.toFixed(3) : '-'}</td>
      </tr>
    `).join('');
  } catch(e) {
    document.getElementById('history-body').innerHTML = '<tr><td colspan="4">Erreur chargement</td></tr>';
  }
}

loadLatest();
loadStats();
loadHistory();
