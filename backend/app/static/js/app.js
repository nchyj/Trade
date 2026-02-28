const getJSON = (url, options = {}) => fetch(url, options).then(r => r.json());

async function loadMetrics() {
  const data = await getJSON('/api/dashboard/metrics');
  const metrics = document.getElementById('metrics');
  metrics.innerHTML = `
    <div class="metric">现金: ${data.cash.toFixed(2)}</div>
    <div class="metric">权益: ${data.equity.toFixed(2)}</div>
    <div class="metric">冻结资金: ${data.frozen_cash.toFixed(2)}</div>
    <div class="metric">策略数: ${data.strategy_count}</div>
    <div class="metric">订单数: ${data.order_count}</div>
    <div class="metric">持仓数: ${data.position_count}</div>
  `;
}

async function loadMarket() {
  const symbol = document.getElementById('symbolSelect').value;
  const data = await getJSON(`/api/market-data?symbol=${symbol}`);
  const tbody = document.querySelector('#marketTable tbody');
  tbody.innerHTML = data.map(d => `<tr><td>${d.trade_date}</td><td>${d.open}</td><td>${d.high}</td><td>${d.low}</td><td>${d.close}</td><td>${d.volume}</td></tr>`).join('');
}

async function loadStrategies() {
  const data = await getJSON('/api/strategies');
  document.getElementById('strategyList').innerHTML = data.map(s => `<li>#${s.id} ${s.name} - ${s.status}</li>`).join('');
}

async function loadBacktests() {
  const data = await getJSON('/api/backtests');
  document.getElementById('backtestList').innerHTML = data.slice(0, 5).map(r => `<li>#${r.id} 策略${r.strategy_id} ${r.symbol} 收益:${(r.total_return * 100).toFixed(2)}%</li>`).join('');
}

async function loadOrders() {
  const data = await getJSON('/api/orders');
  document.querySelector('#orderTable tbody').innerHTML = data.slice(0, 10).map(o => `<tr><td>${o.id}</td><td>${o.symbol}</td><td>${o.side}</td><td>${o.quantity}</td><td>${o.price}</td><td>${o.status}</td></tr>`).join('');
}

async function loadPositionsAndAccount() {
  const account = await getJSON('/api/account');
  const positions = await getJSON('/api/positions');
  document.getElementById('accountInfo').textContent = JSON.stringify(account, null, 2);
  document.getElementById('positionList').innerHTML = positions.map(p => `<li>${p.symbol}: ${p.quantity}股, 成本${p.avg_price}</li>`).join('');
}

async function loadAudit() {
  const logs = await getJSON('/api/audit-logs');
  document.getElementById('auditList').innerHTML = logs.slice(0, 8).map(l => `<li>[${l.module}] ${l.action} - ${l.detail}</li>`).join('');
}

async function loadRiskEvents() {
  const events = await getJSON('/api/risk/events');
  document.getElementById('riskList').innerHTML = events.slice(0, 5).map(e => `<li>${e.level}: ${e.message}</li>`).join('');
}

async function refreshAll() {
  await Promise.all([
    loadMetrics(), loadMarket(), loadStrategies(), loadBacktests(),
    loadOrders(), loadPositionsAndAccount(), loadAudit(), loadRiskEvents()
  ]);
}

document.getElementById('refreshAll').addEventListener('click', refreshAll);
document.getElementById('symbolSelect').addEventListener('change', loadMarket);

document.getElementById('strategyForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await getJSON('/api/strategies', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(Object.fromEntries(fd.entries())),
  });
  e.target.reset();
  refreshAll();
});

document.getElementById('backtestForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await getJSON('/api/backtests/run', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(Object.fromEntries(fd.entries())),
  });
  refreshAll();
});

document.getElementById('orderForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await getJSON('/api/orders/paper', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(Object.fromEntries(fd.entries())),
  });
  refreshAll();
});

document.getElementById('riskBtn').addEventListener('click', async () => {
  await getJSON('/api/risk/evaluate', { method: 'POST' });
  refreshAll();
});

refreshAll();
