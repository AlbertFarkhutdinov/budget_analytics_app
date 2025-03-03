from fastapi import FastAPI
import uvicorn

from .auth import auth_router
from .entries import entries_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(entries_router, prefix="/entries")


def start_backend():
    uvicorn.run(
        app="budget_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
