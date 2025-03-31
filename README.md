# budget_analytics_app

![GitHub repo size](https://img.shields.io/github/issues/AlbertFarkhutdinov/budget_analytics_app)
![GitHub contributors](https://img.shields.io/github/contributors/AlbertFarkhutdinov/budget_analytics_app)
![GitHub forks](https://img.shields.io/github/forks/AlbertFarkhutdinov/budget_analytics_app)
![GitHub License](https://img.shields.io/github/license/AlbertFarkhutdinov/budget_analytics_app)
![GitHub Repo stars](https://img.shields.io/github/stars/AlbertFarkhutdinov/budget_analytics_app)

`budget_analytics_app` is a web application 
designed for personal finance tracking and analytics. 

## Installing `budget_analytics_app`

1. Install Python package and project manager [uv](https://docs.astral.sh/uv/);
2. Clone the repository:
    ```
    git clone https://github.com/AlbertFarkhutdinov/budget_analytics_app.git
    cd budget_analytics_app
    ```
3. Create virtual environment and install dependencies:
    ```
    uv sync --frozen
    ```
4. Add files with environment variables.

## Environment variables

1. `backend/src/backend/auth_app/.env` contains AWS Cognito settings:
   ```
   COGNITO_USER_POOL_ID="Input your user pool ID"
   COGNITO_CLIENT_ID="Input your client ID"
   COGNITO_REGION="Input your region, e.g., us-east-1"
   COGNITO_CLIENT_SECRET="Input your secret"
   ```
2. `backend/src/backend/entries_app/.env` contains PostgreSQL settings:
   ```
   DB_USER="Input your username"
   DB_PASSWORD="Input your password"
   DB_HOST="Input the database host"
   DB_PORT="Input the database port, e.g., 5432"
   DB_NAME="Input the database name"
   ```
3. `backend/src/backend/reports_app/.env` contains AWS S3 settings:
   ```
   S3_ENDPOINT_URL=https://s3.amazonaws.com
   S3_BUCKET=bucket-name
   S3_ACCESS_KEY_ID=INPUT_YOUR_ACCESS_KEY
   S3_SECRET_ACCESS_KEY=INPUT_YOUR_SECRET_ACCESS_KEY
   ```

## Running `budget_analytics_app`

1. To run backend, run the following command in the root directory:
   ```
   uv run backend
   ``` 
   Example of successful output:
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```
2. To run frontend, run the following command in the root directory:
   ```
   uv run frontend
   ```
   Example of successful output:
   ```
   You can now view your Streamlit app in your browser.
   
   Local URL: http://localhost:8501
   Network URL: ...
   ```

## Contributing to `budget_analytics_app`
To contribute to `budget_analytics_app`, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`.
4. Push to the original branch: `git push origin <project_name>/<location>`.
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contributors

* [@AlbertFarkhutdinov](https://github.com/AlbertFarkhutdinov) 

## Contact

If you want to contact me you can reach me at `albertfarhutdinov@gmail.com`.

## License
This project is licensed under the [MIT License](https://github.com/AlbertFarkhutdinov/budget_analytics_app/blob/main/LICENSE).