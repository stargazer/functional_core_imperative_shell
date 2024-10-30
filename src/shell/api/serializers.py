from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskSerializer(BaseModel):
    """
    Defines the serializer class for `Task` instances.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    completed_at: Optional[datetime] = None
    created_at: datetime