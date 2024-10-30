from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, AwareDatetime


class TaskModel(BaseModel):
    """
    This class defines the TaskModel, which is one of our domain concepts.
    """

    model_config = ConfigDict(from_attributes=True)

    # The `id` field should be computed in the `shell` layer, as it's a database concept.
    # In the `core` layer it should remain optional since it's irrelevant, and in order for us to be able to represent both new and existing models
    id: Optional[int] = None

    name: str
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None