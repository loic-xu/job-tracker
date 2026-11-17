from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    """Input model for creating a new job application (POST)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    company: str
    title: str
    type: str = ""
    application_date: str = ""
    status: str = "To Apply"
    notes: str = ""
    link: str


class ApplicationUpdate(BaseModel):
    """Input model for updating an existing job application (PUT)."""

    company: str | None = None
    title: str | None = None
    type: str | None = None
    application_date: str | None = None
    status: str | None = None
    notes: str | None = None
    link: str | None = None


class ApplicationResponse(BaseModel):
    """Response model for a job application (GET)."""

    id: int
    company: str
    title: str
    type: str
    application_date: str
    status: str
    notes: str
    link: str


class StatsResponse(BaseModel):
    """Response model for statistics."""

    total: int
    by_status: dict[str, int]
