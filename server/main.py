from fastapi import FastAPI, HTTPException, status, Request
from server.models import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    StatsResponse,
)
from server.csv_repository import CandidatureRepository
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from server.exceptions import CSVLockedError
import logging

app = FastAPI(
    title="Job Tracker API",
    description="API for tracking and managing job applications.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CSVLockedError)
def csv_locked_exception_handler(request: Request, exc: CSVLockedError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "The CSV file is locked, close it."},
    )


candidature = CandidatureRepository()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.get("/api/health", status_code=status.HTTP_200_OK)
def get_health():
    """
    Check server health status.
    """
    return {"status": "ok"}


@app.get(
    "/api/applications",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
)
def get_applications():
    """
    Retrieve all job applications.
    """
    return candidature.get_all()


@app.get("/api/stats", response_model=StatsResponse, status_code=status.HTTP_200_OK)
def get_stats():
    """
    Retrieve application metrics and aggregated stats.
    """
    return candidature.get_stats()


@app.post(
    "/api/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_application(application: ApplicationCreate):
    """
    Create a new job application.
    """
    return candidature.add(application.model_dump())


@app.put(
    "/api/applications/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
)
def update_application(app_id: int, application: ApplicationUpdate):
    """
    Update an existing job application by ID (partial or full update).
    """
    update_data = application.model_dump(exclude_unset=True)
    updated_app = candidature.update(app_id, update_data)
    if updated_app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application number {app_id} was not found.",
        )

    return updated_app


@app.delete("/api/applications/{app_id}", status_code=status.HTTP_200_OK)
def delete_application(app_id: int):
    """
    Delete a job application by ID.
    """
    success = candidature.delete(app_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application number {app_id} was not found.",
        )
    return {"ok": True}
