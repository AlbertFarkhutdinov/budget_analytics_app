"""
A backend part of the Budget Analysis Service.

It provides authentication, financial reporting,
and expense tracking functionalities through various subpackages.

Subpackages
-----------
- api: Provides FastAPI endpoints for interacting with the backend.
- auth_app: Handles user authentication and authorization using AWS Cognito.
- entries_app: Manages budget entries, transactions, and related data.
- reports_app: Generates and manages financial reports.

Examples
--------
To start the backend, run:
```
python -m backend.api.run_backend
```

"""
