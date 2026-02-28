from flask import Blueprint, jsonify, render_template, request

from ..db import SessionLocal
from ..models import AuditLog
from ..services import (
    audit_service,
    backtest_service,
    dashboard_service,
    market_service,
    risk_service,
    scheduler_service,
    strategy_service,
    trading_service,
)

api_bp = Blueprint('api', __name__)


@api_bp.errorhandler(ValueError)
def handle_value_error(err):
    return jsonify({'error': str(err)}), 400


@api_bp.get('/')
def index():
    return render_template('index.html')


@api_bp.get('/api/health')
def health_check():
    return jsonify({'status': 'ok'})


@api_bp.get('/api/market-data')
def get_market_data():
    symbol = request.args.get('symbol')
    return jsonify(market_service.list_symbols_data(symbol))


@api_bp.get('/api/market-overview')
def market_overview():
    return jsonify(scheduler_service.list_market_overview())


@api_bp.get('/api/strategies')
def list_strategies():
    return jsonify(strategy_service.list_strategies())


@api_bp.get('/api/strategies/<int:strategy_id>')
def get_strategy(strategy_id: int):
    return jsonify(strategy_service.get_strategy(strategy_id))


@api_bp.post('/api/strategies')
def create_strategy():
    payload = request.get_json(force=True)
    strategy = strategy_service.create_strategy(payload)
    audit_service.log_event('strategy', 'create', f"创建策略: {strategy['name']}")
    return jsonify(strategy), 201


@api_bp.put('/api/strategies/<int:strategy_id>/code')
def update_strategy_code(strategy_id: int):
    payload = request.get_json(force=True)
    updated = strategy_service.update_strategy_code(strategy_id, payload['code'])
    audit_service.log_event('strategy', 'update_code', f"更新策略代码: {updated['name']}")
    return jsonify(updated)


@api_bp.get('/api/backtests')
def list_backtests():
    return jsonify(backtest_service.list_backtests())


@api_bp.post('/api/backtests/run')
def run_backtest():
    payload = request.get_json(force=True)
    result = backtest_service.run_backtest(
        strategy_id=int(payload['strategy_id']),
        symbol=payload['symbol'],
        start_date=payload['start_date'],
        end_date=payload['end_date'],
        init_cash=float(payload['init_cash']),
        benchmark=payload['benchmark'],
        frequency=payload['frequency'],
    )
    audit_service.log_event('backtest', 'run', f"策略{result['strategy_id']}回测{result['symbol']}")
    return jsonify(result)


@api_bp.get('/api/orders')
def list_orders():
    return jsonify(trading_service.list_orders())


@api_bp.post('/api/orders/paper')
def paper_order():
    payload = request.get_json(force=True)
    result = trading_service.place_paper_order(payload)
    audit_service.log_event('paper_trading', 'place_order', f"{result['side']} {result['symbol']} {result['quantity']}")
    return jsonify(result)


@api_bp.get('/api/positions')
def list_positions():
    return jsonify(trading_service.list_positions())


@api_bp.get('/api/account')
def account():
    return jsonify(trading_service.get_account())


@api_bp.post('/api/risk/evaluate')
def evaluate_risk():
    result = risk_service.evaluate_risk()
    audit_service.log_event('risk', 'evaluate', f"风险评估触发，事件数:{len(result['events'])}")
    return jsonify(result)


@api_bp.get('/api/risk/events')
def risk_events():
    return jsonify(risk_service.list_risk_events())


@api_bp.get('/api/audit-logs')
def audit_logs():
    from sqlalchemy import select

    session = SessionLocal()
    try:
        rows = session.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all()
        return jsonify([
            {
                'id': r.id,
                'module': r.module,
                'action': r.action,
                'detail': r.detail,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ])
    finally:
        session.close()


@api_bp.get('/api/dashboard/metrics')
def dashboard_metrics():
    return jsonify(dashboard_service.get_dashboard_metrics())


@api_bp.get('/api/scheduler/tasks')
def list_tasks():
    return jsonify(scheduler_service.list_tasks())


@api_bp.post('/api/scheduler/tasks')
def create_task():
    payload = request.get_json(force=True)
    task = scheduler_service.create_task(payload)
    audit_service.log_event('scheduler', 'create_task', f"创建任务#{task['id']} {task['name']}")
    return jsonify(task), 201


@api_bp.post('/api/scheduler/tasks/<int:task_id>/start')
def start_task(task_id: int):
    return jsonify(scheduler_service.start_task(task_id))


@api_bp.post('/api/scheduler/tasks/<int:task_id>/stop')
def stop_task(task_id: int):
    return jsonify(scheduler_service.stop_task(task_id))


@api_bp.post('/api/scheduler/tasks/<int:task_id>/run-once')
def run_task_once(task_id: int):
    return jsonify(scheduler_service.run_task_once(task_id))
