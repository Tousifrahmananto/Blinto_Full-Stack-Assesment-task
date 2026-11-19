from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Year = Annotated[int, Field(strict=True, ge=1000, le=9999)]
Runtime = Annotated[int, Field(strict=True, ge=1, le=300)]
Watched = Annotated[bool, Field(strict=True)]
MovieId = Annotated[int, Field(strict=True, gt=0)]


class MovieSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_year: int
    runtime_minutes: int
    watched: bool


class MovieDetails(MovieSummary):
    prerequisite_ids: list[int]


class MovieCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title
    release_year: Year
    runtime_minutes: Runtime
    watched: Watched = False
    prerequisite_ids: list[MovieId] = Field(default_factory=list)


class MoviePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    release_year: Year | None = None
    runtime_minutes: Runtime | None = None
    watched: Watched | None = None
    prerequisite_ids: list[MovieId] | None = None

    @model_validator(mode="after")
    def reject_null_fields(self):
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Omit unchanged fields. Use [] to clear prerequisites.")
        return self


class RewatchPlan(BaseModel):
    movies: list[MovieSummary]
    watched_count: int
    remaining_runtime_minutes: int


BundleSize = Annotated[int, Field(strict=True, ge=1, le=500)]


class CinemaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    bundle_sizes: Annotated[list[BundleSize], Field(min_length=1, max_length=10)]

    @model_validator(mode="after")
    def reject_duplicate_sizes(self):
        if len(set(self.bundle_sizes)) != len(self.bundle_sizes):
            raise ValueError("Bundle sizes must be distinct.")
        return self


class CinemaDetails(BaseModel):
    id: int
    name: str
    bundle_sizes: list[int]


class BundleQuantity(BaseModel):
    size: int
    quantity: int


class BookingQuote(BaseModel):
    possible: bool
    bundle_count: int | None
    bundles: list[BundleQuantity]
