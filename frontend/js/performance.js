// ─── STATE ───────────────────────────────────────────────────────────────────
let workers = [];
let searchQ = '';
let roleFilter = 'all';
let profileChart = null;

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function avatarColor(name) {
  const palettes = [
    ['#534AB7','#EEEDFE'], ['#0F6E56','#E1F5EE'], ['#993C1D','#FAECE7'],
    ['#993556','#FBEAF0'], ['#185FA5','#E6F1FB']
  ];
  return palettes[name.charCodeAt(0) % 5];
}

function roleClass(role) {
  const map = { analyst:'role-analyst', reviewer:'role-reviewer', cw:'role-cw', tl:'role-tl' };
  return map[role?.toLowerCase()] || 'role-analyst';
}

function tierClass(tier) {
  return {
    TOP_PERFORMER: 'tier-top', HIGH_PERFORMER: 'tier-high',
    SOLID_PERFORMER: 'tier-solid', AVERAGE_PERFORMER: 'tier-avg',
    LOW_PERFORMER: 'tier-low'
  }[tier] || 'tier-avg';
}

function tierLabel(tier) {
  return (tier || '').replace(/_/g, ' ');
}

// Map quality_signal object → pill appearance
// quality_signal has fields like: signal, label, value, above_average
function qualityPill(qs) {
  if (!qs) return '<span class="signal-pill signal-neutral">—</span>';
  const label = qs.label || qs.signal || 'Unknown';
  const cls = qs.above_average === true ? 'signal-good'
            : qs.above_average === false ? 'signal-warn'
            : 'signal-neutral';
  return `<span class="signal-pill ${cls}">${label}</span>`;
}

function fillColor(pct) {
  if (pct >= 70) return '#1baf7a';
  if (pct >= 40) return '#7F77DD';
  if (pct >= 20) return '#EF9F27';
  return '#F09975';
}

function fmt(v, decimals = 2) {
  if (v === null || v === undefined) return '—';
  return typeof v === 'number' ? v.toFixed(decimals) : v;
}

// ─── API ─────────────────────────────────────────────────────────────────────
async function apiQuery(query) {
  const res = await fetch(`${API_BASE}/performance/run?query=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// ─── ROSTER ──────────────────────────────────────────────────────────────────
function showLoading(msg = 'Loading…') {
  document.getElementById('main-content').innerHTML = `
    <div class="loading-wrap"><div class="spinner"></div>${msg}</div>`;
}

function showError(msg) {
  document.getElementById('main-content').innerHTML = `
    <div class="page-header"><div class="page-title">Performance Agent</div></div>
    <div class="error-box"><i class="ti ti-alert-triangle"></i> ${msg}</div>`;
}

async function loadRoster() {
  showLoading('Fetching team performance…');
  try {
    const data = await apiQuery('List all employees with their performance summary');
    workers = Array.isArray(data) ? data : [data];
    renderRoster();
  } catch (e) {
    showError(`Could not load roster: ${e.message}`);
  }
}

function renderRoster() {
  const filtered = workers.filter(w => {
    const name = (w.employee_name || '').toLowerCase();
    const role = (w.role || '').toLowerCase();
    const mq = name.includes(searchQ.toLowerCase()) || role.includes(searchQ.toLowerCase());
    const mf = roleFilter === 'all' || role === roleFilter;
    return mq && mf;
  });

  const main = document.getElementById('main-content');
  main.innerHTML = '';
  const wrap = document.createElement('div');

  // Collect unique roles for filter dropdown
  const roles = [...new Set(workers.map(w => (w.role || '').toLowerCase()).filter(Boolean))];
  const roleOpts = ['all', ...roles].map(r =>
    `<option value="${r}" ${roleFilter === r ? 'selected' : ''}>${r === 'all' ? 'All roles' : r}</option>`
  ).join('');

  wrap.innerHTML = `
    <div class="page-header">
      <div class="page-title">Performance Agent</div>
      <div class="page-sub">Click a name to view the full profile dashboard.</div>
    </div>
    <div class="search-row">
      <div class="search-box">
        <i class="ti ti-search"></i>
        <input id="search-input" placeholder="Search by name or role…" value="${searchQ}">
      </div>
      <select id="role-filter" class="filter-btn">${roleOpts}</select>
      <button class="filter-btn" id="refresh-btn" style="gap:6px">
        <i class="ti ti-refresh" style="font-size:14px"></i> Refresh
      </button>
    </div>
    <div class="roster-wrap">
      <table class="roster-table">
        <thead><tr>
          <th>Name</th><th>Role</th><th>Quality signal</th><th>Percentile</th>
        </tr></thead>
        <tbody id="roster-body"></tbody>
      </table>
      ${filtered.length === 0 ? '<div class="empty">No workers match your search.</div>' : ''}
    </div>`;
  main.appendChild(wrap);

  const tbody = document.getElementById('roster-body');
  filtered.forEach(w => {
    const [bg, fg] = avatarColor(w.employee_name || '?');
    const pct = Math.round(w.percentile ?? 0);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><div class="name-cell">
        <div class="avatar" style="background:${bg};color:${fg}">${initials(w.employee_name || '?')}</div>
        <span class="name-link">${w.employee_name}</span>
      </div></td>
      <td><span class="role-pill ${roleClass(w.role)}">${w.role}</span></td>
      <td>${qualityPill(w.quality_signal)}</td>
      <td><div class="score-bar-wrap">
        <div class="score-bar"><div class="score-fill" style="width:${pct}%;background:${fillColor(pct)}"></div></div>
        <span class="pct-val">${pct}</span>
      </div></td>`;
    row.querySelector('.name-link').addEventListener('click', e => { e.stopPropagation(); loadProfile(w); });
    row.addEventListener('click', () => loadProfile(w));
    tbody.appendChild(row);
  });

  document.getElementById('search-input').addEventListener('input', e => { searchQ = e.target.value; renderRoster(); });
  document.getElementById('role-filter').addEventListener('change', e => { roleFilter = e.target.value; renderRoster(); });
  document.getElementById('refresh-btn').addEventListener('click', loadRoster);
}

// ─── PROFILE ─────────────────────────────────────────────────────────────────
async function loadProfile(basicW) {
  showLoading(`Loading profile for ${basicW.employee_name}…`);
  try {
    const data = await apiQuery(`Full performance analysis for employee id ${basicW.id}`);
    const w = Array.isArray(data) ? data[0] : data;
    renderProfile(w);
  } catch (e) {
    showError(`Could not load profile: ${e.message}`);
  }
}

function renderProfile(w) {
  if (profileChart) { profileChart.destroy(); profileChart = null; }

  const main = document.getElementById('main-content');
  main.innerHTML = '';
  const wrap = document.createElement('div');
  wrap.className = 'page-pad';

  const [bg, fg] = avatarColor(w.employee_name || '?');
  const pct = Math.round(w.percentile ?? 0);
  const bm = w.benchmark_analysis || {};
  const cap = w.capacity_signal || {};
  const qual = w.quality_signal || {};
  const burn = w.burnout_signal || {};
  const suit = w.suitability_profile || {};
  const flags = w.workforce_flags || {};
  const rec = w.recommendation || {};

  // Build benchmark table rows from benchmark_analysis object
  // Expected shape: { mph: {metric_name, employee_value, role_average, variance, variance_percent, above_average}, rph: {...}, ... }
  const bmRows = Object.entries(bm).map(([key, val]) => {
    if (typeof val !== 'object' || val === null) return '';
    const diff = typeof val.variance === 'number' ? val.variance.toFixed(2) : '—';
    const cls = val.above_average ? 'above' : 'below-c';
    const sym = val.above_average ? '+' : '';
    return `<tr>
      <td>${val.metric_name || key}</td>
      <td>${fmt(val.employee_value)}</td>
      <td>${fmt(val.role_average)}</td>
      <td class="${cls}">${sym}${diff}</td>
    </tr>`;
  }).join('');

  const strengths = (w.key_strengths || []).map(s => `<span class="tag tag-strength">${s}</span>`).join('');
  const improvements = (w.improvement_areas || []).map(s => `<span class="tag tag-improve">${s}</span>`).join('');

  // Radar data — normalise rph to same rough scale as others
  const radarData = [
    Math.round(w.raw_accuracy ?? 0),
    Math.round((w.raw_rating ?? 0)),
    Math.round((w.raw_mph ?? 0) * 10),
    Math.round((w.raw_rph ?? 0) / 1.5),
    Math.round(pct),
  ];

  wrap.innerHTML = `
    <button class="back-btn" id="back-btn"><i class="ti ti-arrow-left" style="font-size:14px"></i> Back to roster</button>

    <div class="profile-header">
      <div class="profile-left">
        <div class="avatar" style="width:46px;height:46px;font-size:15px;background:${bg};color:${fg}">${initials(w.employee_name || '?')}</div>
        <div>
          <div class="profile-name">${w.employee_name}</div>
          <div class="profile-meta">
            <span class="role-pill ${roleClass(w.role)}" style="margin-right:8px">${w.role}</span>
            ID: ${w.id} &nbsp;·&nbsp; Rank ${w.rank_in_role} of ${w.total_in_role} in role
          </div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span class="tier-badge ${tierClass(w.performance_tier)}">${tierLabel(w.performance_tier)}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.35)">Deployment score: ${fmt(w.deployment_score, 1)}</span>
      </div>
    </div>

    ${w.executive_summary ? `<div class="summary-box">${w.executive_summary}</div>` : ''}

    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-label">Performance score</div>
        <div class="stat-val">${fmt(w.performance_score, 1)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Percentile</div>
        <div class="stat-val">${pct}</div>
        <div class="stat-sub">Top ${100 - pct + 1}% of all</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Raw accuracy</div>
        <div class="stat-val">${fmt(w.raw_accuracy, 1)}<span style="font-size:14px;color:rgba(255,255,255,0.3)">/100</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Raw rating</div>
        <div class="stat-val">${fmt(w.raw_rating, 1)}<span style="font-size:14px;color:rgba(255,255,255,0.3)">/100</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Raw Mph</div>
        <div class="stat-val">${fmt(w.raw_mph)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Raw Rph</div>
        <div class="stat-val">${fmt(w.raw_rph)}</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">Performance radar</div>
        <div class="chart-sub">vs role average</div>
        <div style="position:relative;height:200px"><canvas id="radar-chart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Benchmark analysis</div>
        <div class="chart-sub">employee vs role average</div>
        <table class="bench-table" style="margin-top:4px">
          <thead><tr><th>Metric</th><th>Yours</th><th>Role avg</th><th>vs avg</th></tr></thead>
          <tbody>${bmRows || '<tr><td colspan="4" style="color:rgba(255,255,255,0.3)">No benchmark data</td></tr>'}</tbody>
        </table>
      </div>
    </div>

    <div class="two-col">
      <div class="section-card">
        <div class="section-head">Signals</div>
        <div class="kv-row"><span class="kv-key">Quality</span><span class="kv-val">${qualityPill(qual)}</span></div>
        <div class="kv-row"><span class="kv-key">Capacity</span><span class="kv-val">${qualityPill(cap)}</span></div>
        <div class="kv-row"><span class="kv-key">Burnout</span><span class="kv-val">${qualityPill(burn)}</span></div>
      </div>
      <div class="section-card">
        <div class="section-head">Workforce flags</div>
        ${Object.entries(flags).map(([k, v]) =>
          `<div class="kv-row"><span class="kv-key">${k.replace(/_/g,' ')}</span><span class="kv-val">${v === true ? '<span style="color:#F09975">Yes</span>' : v === false ? '<span style="color:#5DCAA5">No</span>' : v ?? '—'}</span></div>`
        ).join('') || '<div style="color:rgba(255,255,255,0.3);font-size:13px">No flags</div>'}
      </div>
    </div>

    <div class="two-col">
      <div class="section-card">
        <div class="section-head">Key strengths</div>
        <div class="tag-list">${strengths || '<span style="color:rgba(255,255,255,0.3);font-size:13px">None listed</span>'}</div>
      </div>
      <div class="section-card">
        <div class="section-head">Improvement areas</div>
        <div class="tag-list">${improvements || '<span style="color:rgba(255,255,255,0.3);font-size:13px">None listed</span>'}</div>
      </div>
    </div>

    <div class="section-card">
      <div class="section-head">Suitability profile</div>
      ${Object.entries(suit).map(([k, v]) =>
        `<div class="kv-row"><span class="kv-key">${k.replace(/_/g,' ')}</span><span class="kv-val">${v ?? '—'}</span></div>`
      ).join('') || '<div style="color:rgba(255,255,255,0.3);font-size:13px">No data</div>'}
    </div>

    <div class="section-card">
      <div class="section-head">Recommendation</div>
      ${Object.entries(rec).map(([k, v]) =>
        `<div class="kv-row"><span class="kv-key">${k.replace(/_/g,' ')}</span><span class="kv-val">${v ?? '—'}</span></div>`
      ).join('') || '<div style="color:rgba(255,255,255,0.3);font-size:13px">No recommendation</div>'}
    </div>`;

  main.appendChild(wrap);
  document.getElementById('back-btn').addEventListener('click', () => renderRoster());

  // Radar chart — role average approximated as mid-range; swap with real data if available
  setTimeout(() => {
    const ctx = document.getElementById('radar-chart');
    if (!ctx) return;
    profileChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Accuracy', 'Rating', 'Mph ×10', 'Rph /1.5', 'Percentile'],
        datasets: [
          {
            label: w.employee_name,
            data: radarData,
            borderColor: '#7F77DD',
            backgroundColor: 'rgba(127,119,221,0.15)',
            borderWidth: 2,
            pointBackgroundColor: '#7F77DD',
            pointRadius: 4
          },
          {
            label: 'Role avg',
            data: [
              bm.accuracy?.role_average ?? 85,
              bm.rating?.role_average ?? 75,
              (bm.mph?.role_average ?? 5) * 10,
              (bm.rph?.role_average ?? 45) / 1.5,
              50
            ],
            borderColor: 'rgba(255,255,255,0.2)',
            backgroundColor: 'rgba(255,255,255,0.03)',
            borderWidth: 1,
            borderDash: [4, 3],
            pointRadius: 2,
            pointBackgroundColor: 'rgba(255,255,255,0.3)'
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1a1a2e', titleColor: '#fff', bodyColor: 'rgba(255,255,255,0.6)' } },
        scales: { r: {
          grid: { color: 'rgba(255,255,255,0.07)' },
          angleLines: { color: 'rgba(255,255,255,0.07)' },
          pointLabels: { color: 'rgba(255,255,255,0.5)', font: { size: 10 } },
          ticks: { display: false }
        }}
      }
    });
  }, 100);
}

// ─── BOOT ─────────────────────────────────────────────────────────────────────
loadRoster();