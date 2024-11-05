from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from .schema import Base


engine = create_engine("postgresql+psycopg2://username:password@postgres:5432/db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_models() -> None:
    """
    Creates the DB tables, if they don't exist
    """

    Base.metadata.create_all(bind=engine)


def get_sync_db_session():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()