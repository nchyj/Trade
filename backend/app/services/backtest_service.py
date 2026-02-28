from sqlalchemy import select

from ..db import SessionLocal
from ..models import BacktestResult, MarketData, Strategy


def _safe_load_strategy(code: str):
    env = {'__builtins__': {'len': len, 'sum': sum, 'min': min, 'max': max, 'abs': abs, 'range': range}}
    local_env = {}
    exec(code, env, local_env)
    initialize = local_env.get('initialize')
    handle_data = local_env.get('handle_data')
    if not callable(initialize) or not callable(handle_data):
        raise ValueError('策略代码必须实现 initialize(context) 和 handle_data(context, data)')
    return initialize, handle_data


def _calc_max_drawdown(equity_curve):
    peak = equity_curve[0]
    mdd = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        dd = (value - peak) / peak if peak else 0
        mdd = min(mdd, dd)
    return mdd


def _calc_trade_stats(trade_pnls):
    if not trade_pnls:
        return 0.0, 0.0
    wins = [x for x in trade_pnls if x > 0]
    losses = [x for x in trade_pnls if x < 0]
    win_rate = len(wins) / len(trade_pnls)
    if not losses:
        pl_ratio = float('inf')
    else:
        pl_ratio = (sum(wins) / max(len(wins), 1)) / abs(sum(losses) / len(losses))
    return win_rate, pl_ratio


def run_backtest(strategy_id: int, symbol: str, start_date: str, end_date: str, init_cash: float, benchmark: str, frequency: str):
    session = SessionLocal()
    try:
        strategy = session.scalars(select(Strategy).where(Strategy.id == strategy_id)).first()
        if not strategy:
            raise ValueError('策略不存在')

        candles = session.scalars(
            select(MarketData)
            .where(MarketData.symbol == symbol)
            .where(MarketData.trade_date >= start_date)
            .where(MarketData.trade_date <= end_date)
            .order_by(MarketData.trade_date)
        ).all()
        if len(candles) < 2:
            raise ValueError('样本数量不足，无法回测。')

        initialize, handle_data = _safe_load_strategy(strategy.code)

        context = {'signal': 0}
        initialize(context)

        cash = float(init_cash)
        position = 0
        entry_price = 0.0
        equity_curve = []
        trade_pnls = []

        for candle in candles:
            bar = {
                'symbol': candle.symbol,
                'trade_date': candle.trade_date,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
            }
            handle_data(context, bar)
            signal = context.get('signal', 0)
            close = candle.close

            if signal > 0 and position == 0:
                position = int(cash // close)
                if position > 0:
                    cash -= position * close
                    entry_price = close
            elif signal < 0 and position > 0:
                cash += position * close
                trade_pnls.append((close - entry_price) * position)
                position = 0
                entry_price = 0.0

            equity = cash + position * close
            equity_curve.append(equity)

        if position > 0:
            last_close = candles[-1].close
            trade_pnls.append((last_close - entry_price) * position)
            cash += position * last_close
            position = 0
            equity_curve[-1] = cash

        total_return = (equity_curve[-1] - init_cash) / init_cash
        max_drawdown = _calc_max_drawdown(equity_curve)
        win_rate, pl_ratio = _calc_trade_stats(trade_pnls)
        sharpe = round((total_return / max(abs(max_drawdown), 0.01)) * 0.9, 4)

        result = BacktestResult(
            strategy_id=strategy_id,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            benchmark=benchmark,
            frequency=frequency,
            init_cash=init_cash,
            total_return=round(total_return, 4),
            max_drawdown=round(max_drawdown, 4),
            win_rate=round(win_rate, 4),
            profit_loss_ratio=round(pl_ratio if pl_ratio != float('inf') else 999.0, 4),
            sharpe=sharpe,
        )
        session.add(result)
        session.commit()
        session.refresh(result)

        return {
            'id': result.id,
            'strategy_id': strategy_id,
            'symbol': symbol,
            'benchmark': benchmark,
            'frequency': frequency,
            'init_cash': init_cash,
            'total_return': result.total_return,
            'max_drawdown': result.max_drawdown,
            'win_rate': result.win_rate,
            'profit_loss_ratio': result.profit_loss_ratio,
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
                'benchmark': r.benchmark,
                'frequency': r.frequency,
                'init_cash': r.init_cash,
                'total_return': r.total_return,
                'max_drawdown': r.max_drawdown,
                'win_rate': r.win_rate,
                'profit_loss_ratio': r.profit_loss_ratio,
                'sharpe': r.sharpe,
                'created_at': r.created_at.isoformat(),
            }
            for r in session.scalars(select(BacktestResult).order_by(BacktestResult.id.desc())).all()
        ]
    finally:
        session.close()
