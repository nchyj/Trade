from sqlalchemy import select

from ..db import SessionLocal
from ..models import Account, Order, Position


def list_orders():
    session = SessionLocal()
    try:
        orders = session.scalars(select(Order).order_by(Order.id.desc())).all()
        return [
            {
                'id': o.id,
                'symbol': o.symbol,
                'side': o.side,
                'quantity': o.quantity,
                'price': o.price,
                'status': o.status,
                'created_at': o.created_at.isoformat(),
            }
            for o in orders
        ]
    finally:
        session.close()


def list_positions():
    session = SessionLocal()
    try:
        rows = session.scalars(select(Position).order_by(Position.symbol)).all()
        return [
            {
                'symbol': p.symbol,
                'quantity': p.quantity,
                'avg_price': p.avg_price,
                'market_value': p.market_value,
            }
            for p in rows
        ]
    finally:
        session.close()


def get_account():
    session = SessionLocal()
    try:
        account = session.scalars(select(Account).limit(1)).first()
        return {
            'cash': account.cash,
            'equity': account.equity,
            'frozen_cash': account.frozen_cash,
            'updated_at': account.updated_at.isoformat(),
        }
    finally:
        session.close()


def place_paper_order(payload: dict):
    session = SessionLocal()
    try:
        symbol = payload['symbol']
        side = payload['side'].lower()
        qty = int(payload['quantity'])
        price = float(payload['price'])
        amount = qty * price

        account = session.scalars(select(Account).limit(1)).first()
        if account is None:
            raise ValueError('账户未初始化')

        position = session.scalars(select(Position).where(Position.symbol == symbol)).first()
        status = 'filled'

        if side == 'buy':
            if account.cash < amount:
                status = 'rejected'
            else:
                account.cash -= amount
                if position:
                    total_qty = position.quantity + qty
                    position.avg_price = (position.avg_price * position.quantity + amount) / total_qty
                    position.quantity = total_qty
                    position.market_value = total_qty * price
                else:
                    session.add(Position(symbol=symbol, quantity=qty, avg_price=price, market_value=amount))
        elif side == 'sell':
            if not position or position.quantity < qty:
                status = 'rejected'
            else:
                position.quantity -= qty
                proceeds = amount
                account.cash += proceeds
                position.market_value = position.quantity * price
                if position.quantity == 0:
                    session.delete(position)
        else:
            raise ValueError('side必须是buy或sell')

        account.equity = account.cash + sum(p.market_value for p in session.scalars(select(Position)).all())

        order = Order(symbol=symbol, side=side, quantity=qty, price=price, status=status)
        session.add(order)
        session.commit()
        session.refresh(order)
        return {
            'id': order.id,
            'status': status,
            'symbol': symbol,
            'side': side,
            'quantity': qty,
            'price': price,
        }
    finally:
        session.close()
