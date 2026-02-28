from datetime import datetime
import threading
import time

from sqlalchemy import select

from ..db import SessionLocal
from ..models import MarketData, MarketOverview, ScheduledTask
from .audit_service import log_event

_running_flags: dict[int, bool] = {}
_threads: dict[int, threading.Thread] = {}


def _snapshot_market_overview(session):
    major_indices = ['000001.SZ', '399001.SZ']
    created = 0
    for symbol in major_indices:
        bars = session.scalars(
            select(MarketData)
            .where(MarketData.symbol == symbol)
            .order_by(MarketData.trade_date.desc())
            .limit(2)
        ).all()
        if len(bars) < 2:
            continue
        latest, prev = bars[0], bars[1]
        change_pct = (latest.close - prev.close) / prev.close
        session.add(MarketOverview(
            trade_date=latest.trade_date,
            index_symbol=symbol,
            close=latest.close,
            change_pct=round(change_pct, 4),
            turnover=latest.volume,
            source='scheduled_pull',
        ))
        created += 1
    return created


def run_task_once(task_id: int):
    session = SessionLocal()
    try:
        task = session.scalars(select(ScheduledTask).where(ScheduledTask.id == task_id)).first()
        if not task:
            raise ValueError('任务不存在')

        detail = ''
        if task.task_type == 'market_pull':
            count = _snapshot_market_overview(session)
            detail = f'拉取A股大盘快照{count}条'
        elif task.task_type == 'strategy_tick':
            detail = f'执行策略定时任务 strategy_id={task.strategy_id}'
        else:
            raise ValueError('未知任务类型')

        task.last_run_at = datetime.utcnow()
        session.commit()
        log_event('scheduler', 'run_once', f'task#{task.id} {detail}')
        return {'task_id': task.id, 'detail': detail, 'last_run_at': task.last_run_at.isoformat()}
    finally:
        session.close()


def _runner(task_id: int):
    while _running_flags.get(task_id):
        try:
            run_task_once(task_id)
        except Exception as exc:
            log_event('scheduler', 'run_error', f'task#{task_id} error={exc}')
        session = SessionLocal()
        try:
            task = session.scalars(select(ScheduledTask).where(ScheduledTask.id == task_id)).first()
            interval = task.interval_sec if task else 60
        finally:
            session.close()
        time.sleep(max(interval, 1))


def create_task(payload: dict):
    session = SessionLocal()
    try:
        task = ScheduledTask(
            name=payload['name'],
            task_type=payload['task_type'],
            strategy_id=payload.get('strategy_id'),
            interval_sec=int(payload.get('interval_sec', 60)),
            status='stopped',
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return {
            'id': task.id,
            'name': task.name,
            'task_type': task.task_type,
            'strategy_id': task.strategy_id,
            'interval_sec': task.interval_sec,
            'status': task.status,
        }
    finally:
        session.close()


def list_tasks():
    session = SessionLocal()
    try:
        rows = session.scalars(select(ScheduledTask).order_by(ScheduledTask.id.desc())).all()
        return [
            {
                'id': t.id,
                'name': t.name,
                'task_type': t.task_type,
                'strategy_id': t.strategy_id,
                'interval_sec': t.interval_sec,
                'status': t.status,
                'last_run_at': t.last_run_at.isoformat() if t.last_run_at else None,
            }
            for t in rows
        ]
    finally:
        session.close()


def start_task(task_id: int):
    session = SessionLocal()
    try:
        task = session.scalars(select(ScheduledTask).where(ScheduledTask.id == task_id)).first()
        if not task:
            raise ValueError('任务不存在')
        if task.status == 'running':
            return {'task_id': task.id, 'status': task.status}
        task.status = 'running'
        session.commit()
    finally:
        session.close()

    _running_flags[task_id] = True
    thread = threading.Thread(target=_runner, args=(task_id,), daemon=True)
    _threads[task_id] = thread
    thread.start()
    log_event('scheduler', 'start', f'task#{task_id} started')
    return {'task_id': task_id, 'status': 'running'}


def stop_task(task_id: int):
    _running_flags[task_id] = False
    session = SessionLocal()
    try:
        task = session.scalars(select(ScheduledTask).where(ScheduledTask.id == task_id)).first()
        if not task:
            raise ValueError('任务不存在')
        task.status = 'stopped'
        session.commit()
    finally:
        session.close()
    log_event('scheduler', 'stop', f'task#{task_id} stopped')
    return {'task_id': task_id, 'status': 'stopped'}


def list_market_overview():
    session = SessionLocal()
    try:
        rows = session.scalars(select(MarketOverview).order_by(MarketOverview.id.desc()).limit(20)).all()
        return [
            {
                'id': r.id,
                'trade_date': r.trade_date,
                'index_symbol': r.index_symbol,
                'close': r.close,
                'change_pct': r.change_pct,
                'turnover': r.turnover,
                'source': r.source,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]
    finally:
        session.close()
