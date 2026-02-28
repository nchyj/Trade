from sqlalchemy import select

from ..db import SessionLocal
from ..models import Account, Position, RiskEvent


def evaluate_risk():
    session = SessionLocal()
    try:
        account = session.scalars(select(Account).limit(1)).first()
        positions = session.scalars(select(Position)).all()
        events = []

        concentration = 0.0
        if account.equity > 0 and positions:
            concentration = max((p.market_value / account.equity) for p in positions)
            if concentration > 0.5:
                events.append(('warning', f'单标的仓位集中度过高: {concentration:.2%}'))

        if account.cash / max(account.equity, 1) < 0.1:
            events.append(('critical', '账户可用资金低于10%，请降低仓位。'))

        for level, message in events:
            session.add(RiskEvent(level=level, message=message))

        session.commit()

        return {
            'events': [
                {'level': level, 'message': message}
                for level, message in events
            ],
            'concentration': round(concentration, 4),
            'cash_ratio': round(account.cash / max(account.equity, 1), 4),
        }
    finally:
        session.close()


def list_risk_events():
    session = SessionLocal()
    try:
        rows = session.scalars(select(RiskEvent).order_by(RiskEvent.id.desc()).limit(50)).all()
        return [
            {
                'id': r.id,
                'level': r.level,
                'message': r.message,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]
    finally:
        session.close()
