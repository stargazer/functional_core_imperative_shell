from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Task(Base):
    """
    Defines the `Task` class, which defines the `tasks` database table.
    """

    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(128), 
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True), 
        nullable=False,
        default=func.utcnow(),
    )