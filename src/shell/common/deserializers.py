from pydantic import BaseModel, ConfigDict


class TaskCreateDeserializer(BaseModel):
    """
    Defines the model class that is in charge of the deserialization and validation 
    of the request body, for the `POST /tasks` request.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str