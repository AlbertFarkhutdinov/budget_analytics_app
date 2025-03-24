import uvicorn
from fastapi import FastAPI

from budget_analytics_app.backend.auth import auth_router
from budget_analytics_app.backend.entries import entries_router

app = FastAPI()
app.include_router(auth_router, prefix='/auth')
app.include_router(entries_router, prefix='/entries')


def start_backend():
    uvicorn.run(
        app='budget_analytics_app.backend.run_backend:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )


if __name__ == '__main__':
    start_backend()
