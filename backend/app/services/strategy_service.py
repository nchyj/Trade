from sqlalchemy import select

from ..db import SessionLocal
from ..models import Strategy


def list_strategies():
    session = SessionLocal()
    try:
        return [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'status': s.status,
                'created_at': s.created_at.isoformat(),
            }
            for s in session.scalars(select(Strategy).order_by(Strategy.id)).all()
        ]
    finally:
        session.close()


def create_strategy(payload: dict):
    session = SessionLocal()
    try:
        strategy = Strategy(
            name=payload['name'],
            description=payload.get('description', ''),
            status=payload.get('status', 'stopped'),
        )
        session.add(strategy)
        session.commit()
        session.refresh(strategy)
        return {
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'status': strategy.status,
        }
    finally:
        session.close()
