from sqlalchemy import func, select

from ..db import SessionLocal
from ..models import Account, Order, Position, Strategy


def get_dashboard_metrics():
    session = SessionLocal()
    try:
        account = session.scalars(select(Account).limit(1)).first()
        strategy_count = session.scalar(select(func.count(Strategy.id)))
        order_count = session.scalar(select(func.count(Order.id)))
        position_count = session.scalar(select(func.count(Position.id)))

        return {
            'cash': account.cash,
            'equity': account.equity,
            'frozen_cash': account.frozen_cash,
            'strategy_count': strategy_count,
            'order_count': order_count,
            'position_count': position_count,
        }
    finally:
        session.close()
