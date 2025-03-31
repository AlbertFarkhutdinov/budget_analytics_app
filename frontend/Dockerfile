FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY custom-logging /app/custom-logging
COPY frontend /app/frontend

WORKDIR /app/frontend
RUN uv sync --frozen
CMD ["uv", "run", "frontend"]
