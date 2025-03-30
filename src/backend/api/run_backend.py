"""
FastAPI Backend Application Entry Point.

This module initializes and starts the FastAPI application, including
API routers for authentication, budget entries, and reports.

"""
import uvicorn
from fastapi import FastAPI

from backend.api.auth import auth_router
from backend.api.entries import entries_router
from backend.api.reports import reports_router

app = FastAPI()
app.include_router(auth_router, prefix='/auth')
app.include_router(entries_router, prefix='/entries')
app.include_router(reports_router, prefix='/reports')


def start_backend() -> None:
    """
    Start the FastAPI backend using Uvicorn.

    This function runs the application with predefined settings.

    """
    port = 8000
    reload = False
    uvicorn.run(
        app='backend.api.run_backend:app',
        host='127.0.0.1',
        port=port,
        reload=reload,
    )


if __name__ == '__main__':
    start_backend()
