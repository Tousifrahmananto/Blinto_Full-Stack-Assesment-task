from pydantic import BaseModel, ConfigDict


class MovieSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_year: int
    runtime_minutes: int
    watched: bool
