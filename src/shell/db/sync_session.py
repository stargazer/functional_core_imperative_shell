from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shell.db.schema import Base


sync_db_engine = create_engine("postgresql+psycopg2://username:password@postgres:5432/db")
SyncSessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=sync_db_engine)


def init_models() -> None:
    """
    Creates the DB tables, if they don't exist
    """

    Base.metadata.create_all(bind=sync_db_engine)


def get_sync_db_session() -> Iterator[Session]:
    """
    Returns an iterator (in fact, a generator) of `Session` objects.
    """

    with SyncSessionFactory() as session:
        try:
            yield session
        except:
            session.rollback()
            raise