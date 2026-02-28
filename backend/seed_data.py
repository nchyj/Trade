from app.config import Config
from app.db import Base, SessionLocal, init_db
from app.models import Account, MarketData, Strategy


def seed():
    engine = init_db(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        if session.query(Account).count() == 0:
            session.add(Account(cash=1_000_000, equity=1_000_000, frozen_cash=0))

        if session.query(Strategy).count() == 0:
            session.add_all([
                Strategy(name='MA_Cross_A股', description='5/20均线金叉买入死叉卖出', status='running'),
                Strategy(name='RSI_Revert', description='RSI超卖反转策略', status='stopped'),
            ])

        if session.query(MarketData).count() == 0:
            sample = [
                ('000001.SZ', '2024-01-01', 10.0, 10.2, 9.9, 10.1, 1_200_000),
                ('000001.SZ', '2024-01-02', 10.1, 10.4, 10.0, 10.3, 1_300_000),
                ('000001.SZ', '2024-01-03', 10.3, 10.35, 10.1, 10.15, 980_000),
                ('000001.SZ', '2024-01-04', 10.15, 10.5, 10.1, 10.45, 1_600_000),
                ('000001.SZ', '2024-01-05', 10.45, 10.7, 10.4, 10.65, 1_800_000),
                ('600519.SH', '2024-01-01', 1700, 1720, 1698, 1712, 220_000),
                ('600519.SH', '2024-01-02', 1712, 1740, 1705, 1736, 240_000),
                ('399001.SZ', '2024-01-01', 10000, 10200, 9980, 10160, 5_000_000),
                ('399001.SZ', '2024-01-02', 10160, 10280, 10080, 10210, 5_100_000),
            ]
            session.add_all([
                MarketData(symbol=s, trade_date=d, open=o, high=h, low=l, close=c, volume=v)
                for s, d, o, h, l, c, v in sample
            ])

        session.commit()
    finally:
        session.close()


if __name__ == '__main__':
    seed()
    print('Seed completed.')
