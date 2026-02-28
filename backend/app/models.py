from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .db import Base


class MarketData(Base):
    __tablename__ = 'market_data'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    trade_date = Column(String(20), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)


class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    status = Column(String(20), default='stopped')
    created_at = Column(DateTime, default=datetime.utcnow)


class BacktestResult(Base):
    __tablename__ = 'backtest_results'
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=False)
    benchmark = Column(String(20), nullable=False)
    frequency = Column(String(20), nullable=False)
    init_cash = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_loss_ratio = Column(Float, nullable=False)
    sharpe = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    market_value = Column(Float, nullable=False)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    cash = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    frozen_cash = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class RiskEvent(Base):
    __tablename__ = 'risk_events'
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    module = Column(String(50), nullable=False)
    action = Column(String(120), nullable=False)
    detail = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScheduledTask(Base):
    __tablename__ = 'scheduled_tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    task_type = Column(String(30), nullable=False)
    strategy_id = Column(Integer, nullable=True)
    interval_sec = Column(Integer, nullable=False)
    status = Column(String(20), default='stopped')
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketOverview(Base):
    __tablename__ = 'market_overview'
    id = Column(Integer, primary_key=True)
    trade_date = Column(String(20), nullable=False)
    index_symbol = Column(String(20), nullable=False)
    close = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    turnover = Column(Float, nullable=False)
    source = Column(String(30), nullable=False, default='snapshot')
    created_at = Column(DateTime, default=datetime.utcnow)
