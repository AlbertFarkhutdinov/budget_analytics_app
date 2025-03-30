"""
Backend API for Budget Management System.

This package implements a FastAPI-based backend
for handling user authentication, budget entries, and reports.

Modules
-------
    - `auth`: Handles user authentication via AWS Cognito.
    - `entries`: Manages budget entries creation, reading, updating, deletion.
    - `reports`: Provides report generation and retrieval functionality.
    - `run_backend`: Entry point for launching the FastAPI application.

Examples
--------
    To start the backend, run:
    ```
    python -m backend.api.run_backend
    ```

"""
