from sqlalchemy import select

from ..db import SessionLocal
from ..models import MarketData


def list_symbols_data(symbol: str | None = None):
    session = SessionLocal()
    try:
        stmt = select(MarketData).order_by(MarketData.trade_date)
        if symbol:
            stmt = stmt.where(MarketData.symbol == symbol)
        return [
            {
                'id': row.id,
                'symbol': row.symbol,
                'trade_date': row.trade_date,
                'open': row.open,
                'high': row.high,
                'low': row.low,
                'close': row.close,
                'volume': row.volume,
            }
            for row in session.scalars(stmt).all()
        ]
    finally:
        session.close()
