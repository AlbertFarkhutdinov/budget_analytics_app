import uvicorn
from fastapi import FastAPI

from api.auth import auth_router
from api.entries import entries_router
from api.reports import reports_router

app = FastAPI()
app.include_router(auth_router, prefix='/auth')
app.include_router(entries_router, prefix='/entries')
app.include_router(reports_router, prefix='/reports')


def start_backend() -> None:
    port = 8000
    uvicorn.run(
        app='api.run_backend:app',
        host='0.0.0.0',
        port=port,
        reload=True,
    )


if __name__ == '__main__':
    start_backend()
