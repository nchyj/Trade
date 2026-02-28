const getJSON = async (url, options = {}) => {
  const resp = await fetch(url, options);
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || '请求失败');
  return data;
};

function showError(err) {
  alert(err.message || err);
}

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
  const select = document.getElementById('editorStrategySelect');
  select.innerHTML = data.map(s => `<option value="${s.id}">#${s.id} ${s.name}</option>`).join('');
}

async function loadStrategyIntoEditor() {
  const id = document.getElementById('editorStrategySelect').value;
  if (!id) return;
  const s = await getJSON(`/api/strategies/${id}`);
  document.getElementById('strategyCode').value = s.code;
}

async function saveStrategyCode() {
  const id = document.getElementById('editorStrategySelect').value;
  const code = document.getElementById('strategyCode').value;
  await getJSON(`/api/strategies/${id}/code`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ code })
  });
  alert('策略代码已保存');
}

async function loadBacktests() {
  const data = await getJSON('/api/backtests');
  document.getElementById('backtestList').innerHTML = data.slice(0, 5).map(r =>
    `<li>#${r.id} 收益:${(r.total_return * 100).toFixed(2)}% 最大回撤:${(r.max_drawdown * 100).toFixed(2)}% 胜率:${(r.win_rate * 100).toFixed(2)}% 盈亏比:${r.profit_loss_ratio}</li>`
  ).join('');
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

async function loadTasks() {
  const tasks = await getJSON('/api/scheduler/tasks');
  document.getElementById('taskList').innerHTML = tasks.slice(0, 8).map(t =>
    `<li>#${t.id} ${t.name} [${t.task_type}] ${t.interval_sec}s 状态:${t.status}
      <button onclick="taskAction(${t.id}, 'start')">启动</button>
      <button onclick="taskAction(${t.id}, 'stop')">停止</button>
      <button onclick="taskAction(${t.id}, 'run-once')">立即执行</button>
    </li>`).join('');
}

async function loadOverview() {
  const rows = await getJSON('/api/market-overview');
  document.getElementById('overviewList').innerHTML = rows.slice(0, 8).map(r =>
    `<li>${r.trade_date} ${r.index_symbol} 收盘:${r.close} 涨跌:${(r.change_pct * 100).toFixed(2)}% 成交量:${r.turnover}</li>`
  ).join('');
}

window.taskAction = async (id, action) => {
  try {
    await getJSON(`/api/scheduler/tasks/${id}/${action}`, { method: 'POST' });
    refreshAll();
  } catch (e) {
    showError(e);
  }
};

async function refreshAll() {
  await Promise.all([
    loadMetrics(), loadMarket(), loadStrategies(), loadBacktests(),
    loadOrders(), loadPositionsAndAccount(), loadAudit(), loadRiskEvents(),
    loadTasks(), loadOverview()
  ]);
}

document.getElementById('refreshAll').addEventListener('click', () => refreshAll().catch(showError));
document.getElementById('symbolSelect').addEventListener('change', () => loadMarket().catch(showError));
document.getElementById('loadStrategyBtn').addEventListener('click', () => loadStrategyIntoEditor().catch(showError));
document.getElementById('saveCodeBtn').addEventListener('click', () => saveStrategyCode().catch(showError));

document.getElementById('backtestForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    const fd = new FormData(e.target);
    const result = await getJSON('/api/backtests/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(Object.fromEntries(fd.entries())),
    });
    document.getElementById('latestBacktest').textContent =
      `收益 ${(result.total_return * 100).toFixed(2)}% | 最大回撤 ${(result.max_drawdown * 100).toFixed(2)}% | 胜率 ${(result.win_rate * 100).toFixed(2)}% | 盈亏比 ${result.profit_loss_ratio}`;
    refreshAll();
  } catch (err) {
    showError(err);
  }
});

document.getElementById('orderForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    const fd = new FormData(e.target);
    await getJSON('/api/orders/paper', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(Object.fromEntries(fd.entries())),
    });
    refreshAll();
  } catch (err) {
    showError(err);
  }
});

document.getElementById('taskForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    const fd = new FormData(e.target);
    const payload = Object.fromEntries(fd.entries());
    if (!payload.strategy_id) delete payload.strategy_id;
    await getJSON('/api/scheduler/tasks', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    e.target.reset();
    refreshAll();
  } catch (err) {
    showError(err);
  }
});

document.getElementById('riskBtn').addEventListener('click', async () => {
  try {
    await getJSON('/api/risk/evaluate', { method: 'POST' });
    refreshAll();
  } catch (err) {
    showError(err);
  }
});

refreshAll().then(loadStrategyIntoEditor).catch(showError);
