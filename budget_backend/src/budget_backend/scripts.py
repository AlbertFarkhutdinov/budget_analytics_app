import uvicorn


def start_backend():
    uvicorn.run(
        app="budget_backend.auth:app",
        # app="budget_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
