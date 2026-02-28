from sqlalchemy import select

from ..db import SessionLocal
from ..models import Strategy

DEFAULT_STRATEGY_CODE = '''def initialize(context):
    context["short_window"] = 3
    context["long_window"] = 5
    context["signal"] = 0


def handle_data(context, data):
    closes = context.setdefault("closes", [])
    closes.append(data["close"])

    short_w = context["short_window"]
    long_w = context["long_window"]

    if len(closes) < long_w:
        context["signal"] = 0
        return

    short_ma = sum(closes[-short_w:]) / short_w
    long_ma = sum(closes[-long_w:]) / long_w

    if short_ma > long_ma:
        context["signal"] = 1
    elif short_ma < long_ma:
        context["signal"] = -1
    else:
        context["signal"] = 0
'''


def list_strategies():
    session = SessionLocal()
    try:
        return [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'status': s.status,
                'code': s.code,
                'created_at': s.created_at.isoformat(),
            }
            for s in session.scalars(select(Strategy).order_by(Strategy.id)).all()
        ]
    finally:
        session.close()


def get_strategy(strategy_id: int):
    session = SessionLocal()
    try:
        s = session.scalars(select(Strategy).where(Strategy.id == strategy_id)).first()
        if not s:
            raise ValueError('策略不存在')
        return {
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'status': s.status,
            'code': s.code,
        }
    finally:
        session.close()


def create_strategy(payload: dict):
    session = SessionLocal()
    try:
        strategy = Strategy(
            name=payload['name'],
            description=payload.get('description', ''),
            status=payload.get('status', 'stopped'),
            code=payload.get('code', DEFAULT_STRATEGY_CODE),
        )
        session.add(strategy)
        session.commit()
        session.refresh(strategy)
        return {
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'status': strategy.status,
            'code': strategy.code,
        }
    finally:
        session.close()


def update_strategy_code(strategy_id: int, code: str):
    if 'def initialize' not in code or 'def handle_data' not in code:
        raise ValueError('策略代码必须包含 initialize 和 handle_data 两个函数')

    session = SessionLocal()
    try:
        strategy = session.scalars(select(Strategy).where(Strategy.id == strategy_id)).first()
        if not strategy:
            raise ValueError('策略不存在')
        strategy.code = code
        session.commit()
        return {
            'id': strategy.id,
            'name': strategy.name,
            'code': strategy.code,
        }
    finally:
        session.close()
