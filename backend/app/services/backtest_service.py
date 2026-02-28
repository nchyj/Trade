from sqlalchemy import select

from ..db import SessionLocal
from ..models import BacktestResult, MarketData


def run_backtest(strategy_id: int, symbol: str, start_date: str, end_date: str):
    session = SessionLocal()
    try:
        candles = session.scalars(
            select(MarketData)
            .where(MarketData.symbol == symbol)
            .where(MarketData.trade_date >= start_date)
            .where(MarketData.trade_date <= end_date)
            .order_by(MarketData.trade_date)
        ).all()
        if len(candles) < 2:
            raise ValueError('样本数量不足，无法回测。')

        first = candles[0].close
        last = candles[-1].close
        total_return = (last - first) / first
        max_drawdown = min((c.low - c.high) / c.high for c in candles)
        sharpe = round((total_return / max(abs(max_drawdown), 0.01)) * 0.8, 4)

        result = BacktestResult(
            strategy_id=strategy_id,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            total_return=round(total_return, 4),
            max_drawdown=round(max_drawdown, 4),
            sharpe=sharpe,
        )
        session.add(result)
        session.commit()
        session.refresh(result)

        return {
            'id': result.id,
            'strategy_id': strategy_id,
            'symbol': symbol,
            'total_return': result.total_return,
            'max_drawdown': result.max_drawdown,
            'sharpe': result.sharpe,
        }
    finally:
        session.close()


def list_backtests():
    session = SessionLocal()
    try:
        return [
            {
                'id': r.id,
                'strategy_id': r.strategy_id,
                'symbol': r.symbol,
                'start_date': r.start_date,
                'end_date': r.end_date,
                'total_return': r.total_return,
                'max_drawdown': r.max_drawdown,
                'sharpe': r.sharpe,
                'created_at': r.created_at.isoformat(),
            }
            for r in session.scalars(select(BacktestResult).order_by(BacktestResult.id.desc())).all()
        ]
    finally:
        session.close()
