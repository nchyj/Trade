from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False))
engine = None


def init_db(uri: str):
    global engine
    engine = create_engine(uri, echo=False, future=True)
    SessionLocal.configure(bind=engine)
    return engine
