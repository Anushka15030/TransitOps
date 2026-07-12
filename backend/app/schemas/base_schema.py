from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Common config for all schemas: allows constructing from ORM objects."""
    model_config = ConfigDict(from_attributes=True)